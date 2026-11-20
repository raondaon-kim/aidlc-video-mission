"""Speed sampling for video-lab: measure how fast reference videos cut and move.

For each template demo MP4 (catalog.md links) it:
  1. downloads it into samples/videos/ (skips if present)
  2. runs ONE light ffmpeg pass at 320px: per-frame scene score
  3. derives cuts (score >= CUT, at least MIN_GAP apart), average shot length,
     cuts per second and mean motion (average scene score)
  4. makes a 5x2 contact sheet (10 evenly spaced frames) in samples/sheets/
Then writes samples/SAMPLES.md ranked by speed and samples/speed.json.

Memory guard: before each ffmpeg it waits for >= MIN_FREE_GB free RAM (max 60 s),
otherwise stops cleanly and keeps what it measured. One ffmpeg at a time, 1 thread.

Usage: python scripts/sample_speed.py [--only 02,11,24] [--force]
"""
from __future__ import annotations

import argparse
import ctypes
import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / ".claude" / "skills" / "opus-5-5-video-templates" / "catalog.md"
OUT = ROOT / "samples"
VIDS, SHEETS, TMP = OUT / "videos", OUT / "sheets", OUT / "tmp"
URL_RE = re.compile(r"https://cdn\.claudeimagine\.com/uploads/opus-5-5-video/(\d{2})-[a-z0-9-]+\.mp4")

CUT = 0.30        # scene score treated as a cut / hard transition
MIN_GAP = 0.12    # seconds; closer detections are one transition
MIN_FREE_GB = 1.8


def free_gb() -> float:
    class MS(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    try:
        m = MS(); m.dwLength = ctypes.sizeof(MS)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
        return m.ullAvailPhys / 2**30
    except (AttributeError, OSError):
        return 99.0  # non-Windows: no guard


def wait_for_memory() -> bool:
    for _ in range(12):
        if free_gb() >= MIN_FREE_GB:
            return True
        time.sleep(5)
    return False


def catalog_rows() -> dict[str, dict]:
    rows = {}
    for line in CATALOG.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        m = URL_RE.search(line)
        if len(cells) >= 7 and m:
            rows[cells[0]] = {"num": cells[0], "slug": cells[1].strip("`"), "kind": cells[3],
                              "length": cells[4], "format": cells[5],
                              "title": re.sub(r"\*\*(.*?)\*\*.*", r"\1", cells[2]), "url": m.group(0)}
    return rows


def duration(path: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=nw=1:nk=1", str(path)], capture_output=True, text=True)
    return float(r.stdout.strip() or 0)


def scene_scores(path: Path) -> list[tuple[float, float]]:
    TMP.mkdir(parents=True, exist_ok=True)
    out = TMP / "scores.txt"
    out.unlink(missing_ok=True)
    # metadata=print writes to a file; a relative name avoids Windows path escaping in the filter.
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-threads", "1", "-i", str(path),
                    "-vf", "scale=320:-2,select='gte(scene,0)',metadata=print:key=lavfi.scene_score:file=scores.txt",
                    "-an", "-f", "null", "-"], cwd=TMP, check=True)
    scores, t = [], None
    for line in out.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.search(r"pts_time:([\d.]+)", line)
        if m:
            t = float(m.group(1))
        m = re.search(r"lavfi\.scene_score=([\d.]+)", line)
        if m and t is not None:
            scores.append((t, float(m.group(1))))
    return scores


def contact_sheet(path: Path, dur: float, dest: Path) -> None:
    fps = 10 / max(dur, 0.1)
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-threads", "1", "-i", str(path),
                    "-vf", f"fps={fps:.4f},scale=256:-2,tile=5x2:padding=4:color=black",
                    "-frames:v", "1", "-q:v", "4", str(dest)], check=True)


def measure(scores: list[tuple[float, float]], dur: float) -> dict:
    cuts: list[float] = []
    for t, s in scores:
        if s >= CUT and (not cuts or t - cuts[-1] >= MIN_GAP):
            cuts.append(t)
    edges = [0.0, *cuts, dur]
    shots = [b - a for a, b in zip(edges, edges[1:]) if b - a > 0]
    motion = sum(s for _, s in scores) / len(scores) if scores else 0.0
    return {"duration": round(dur, 2), "cuts": len(cuts),
            "cuts_per_sec": round(len(cuts) / dur, 2) if dur else 0,
            "avg_shot": round(sum(shots) / len(shots), 2) if shots else dur,
            "shortest_shot": round(min(shots), 2) if shots else dur,
            "motion": round(motion * 100, 2), "cut_times": [round(c, 2) for c in cuts]}


BURST_GAP = 0.45  # cuts closer than this belong to one rapid-fire burst
BURST_MIN = 3     # at least this many quick gaps in a row


def bursts(cut_times: list[float]) -> list[dict]:
    """Rapid-fire stretches: runs of >= BURST_MIN gaps each <= BURST_GAP."""
    out, run = [], [cut_times[0]] if cut_times else []
    for a, b in zip(cut_times, cut_times[1:]):
        if b - a <= BURST_GAP:
            run.append(b)
            continue
        if len(run) - 1 >= BURST_MIN:
            out.append(run)
        run = [b]
    if len(run) - 1 >= BURST_MIN:
        out.append(run)
    return [{"start": r[0], "end": r[-1], "cuts": len(r),
             "avg_gap": round((r[-1] - r[0]) / (len(r) - 1), 2)} for r in out]


def write_report(results: list[dict]) -> None:
    for r in results:  # speed score: cuts/sec matters most, motion breaks ties
        r["speed"] = round(r["cuts_per_sec"] * 10 + r["motion"], 1)
        r["bursts"] = bursts(r["cut_times"])
    results.sort(key=lambda r: r["speed"], reverse=True)
    (OUT / "speed.json").write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    fast = [r for r in results if r["cuts_per_sec"] > 0]
    avg = lambda k, rs: round(sum(r[k] for r in rs) / len(rs), 2) if rs else 0  # noqa: E731
    top = results[: max(1, len(results) // 3)]
    lines = [
        "# 속도 샘플링 결과", "",
        f"템플릿 데모 {len(results)}개를 측정했다. 컷 = 장면 점수 ≥ {CUT}, 같은 전환은 {MIN_GAP}s 안에서 1개로 셈.",
        "움직임 = 프레임마다 화면이 바뀐 정도의 평균(0~100). 속도 점수 = 초당 컷 × 10 + 움직임.", "",
        "## 상위 1/3 평균 (빠른 영상의 실제 수치)", "",
        "| 항목 | 상위 1/3 | 전체 |", "|---|---|---|",
        f"| 초당 컷 | {avg('cuts_per_sec', top)} | {avg('cuts_per_sec', results)} |",
        f"| 평균 장면 길이(초) | {avg('avg_shot', top)} | {avg('avg_shot', results)} |",
        f"| 가장 짧은 장면(초) | {avg('shortest_shot', top)} | {avg('shortest_shot', results)} |",
        f"| 움직임 | {avg('motion', top)} | {avg('motion', results)} |", "",
        "## 순위", "",
        "| 순위 | # | 템플릿 | 종류 | 길이 | 컷 | 초당 컷 | 평균 장면 | 최단 | 움직임 | 점수 | 한눈에 |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for i, r in enumerate(results, 1):
        lines.append(f"| {i} | {r['num']} | `{r['slug']}` | {r['kind']} | {r['duration']}s | {r['cuts']} | "
                     f"{r['cuts_per_sec']} | {r['avg_shot']}s | {r['shortest_shot']}s | {r['motion']} | "
                     f"{r['speed']} | [시트](sheets/{r['slug']}.jpg) · [영상]({r['url']}) |")
    with_burst = [r for r in results if r["bursts"]]
    lines += ["", "## 리듬: 연속 빠른 컷 구간 (burst)", "",
              f"간격 ≤ {BURST_GAP}s인 컷이 {BURST_MIN}번 이상 이어지는 구간. "
              f"{len(with_burst)}개 영상에 있음.", "",
              "| # | 템플릿 | 구간 | 위치(전체 중) | 컷 수 | 평균 간격 | 그 밖의 평균 장면 |",
              "|---|---|---|---|---|---|---|"]
    for r in with_burst:
        for b in r["bursts"]:
            outside = [x for x in r["cut_times"] if x < b["start"] or x > b["end"]]
            # time outside the burst, shared by the shots outside it
            calm = round((r["duration"] - (b["end"] - b["start"])) / (len(outside) + 1), 2)
            lines.append(f"| {r['num']} | `{r['slug']}` | {b['start']}~{b['end']}s | "
                         f"{round(b['start'] / r['duration'] * 100)}% | {b['cuts']} | {b['avg_gap']}s | {calm}s |")
    lines += ["", f"컷이 잡힌 영상 {len(fast)}개 / {len(results)}개.",
              "컷 시각은 `samples/speed.json`의 `cut_times`, burst는 `bursts`.", ""]
    (OUT / "SAMPLES.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    rows = catalog_rows()
    want = [n.zfill(2) for n in a.only.split(",") if n] or sorted(rows)
    for d in (VIDS, SHEETS):
        d.mkdir(parents=True, exist_ok=True)
    cache = OUT / "speed.json"
    done = {r["num"]: r for r in json.loads(cache.read_text(encoding="utf-8"))} if cache.is_file() and not a.force else {}
    results = dict(done)
    for num in want:
        row = rows.get(num)
        if not row or (num in done and not a.force):
            continue
        vid = VIDS / f"{row['slug']}.mp4"
        if not vid.is_file():
            # The CDN answers 403 to Python's default client; curl is accepted.
            subprocess.run(["curl", "-sSfL", "--max-time", "120", "-o", str(vid), row["url"]], check=True)
        if not wait_for_memory():
            print(f"멈춤: 빈 메모리 {free_gb():.1f}GB < {MIN_FREE_GB}GB. 측정한 것까지 저장.")
            break
        dur = duration(vid)
        m = measure(scene_scores(vid), dur)
        contact_sheet(vid, dur, SHEETS / f"{row['slug']}.jpg")
        results[num] = {**row, **m}
        print(f"{num} {row['slug']}: 컷 {m['cuts']} · 초당 {m['cuts_per_sec']} · 평균 장면 {m['avg_shot']}s · 움직임 {m['motion']} · RAM {free_gb():.1f}GB")
    write_report(list(results.values()))
    print(f"→ {OUT / 'SAMPLES.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
