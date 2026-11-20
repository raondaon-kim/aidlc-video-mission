"""Measured pass/fail checks for the video-mission AI-DLC stages.

  python scripts/mission_check.py <brief|storyboard|music|draft|final> --project <name> --out <dir>

Reads video-lab/projects/<name>/ and writes <out>/video-mission-<stage>-check.json:
  {"mission", "project", "measured_at", "checks": [{"id","label","value","target","pass"}], "pass"}
The AI-DLC sensor re-derives the verdict from `checks`; `pass` here is for people.
Exit code: 0 all pass, 1 some check failed, 2 could not measure (missing input).
Light: ffprobe/ffmpeg reads only (no render). The draft/final rhythm check decodes
the video once at 320 px with one thread (same method as sample_speed.py).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

LAB = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(LAB / "scripts"))

# Targets: video-lab/index/curated.md chapter 2 (approved 2026-11-20).
NORMAL_SCENE = (1.5, 2.5)
BURST_POS = (0.55, 0.75)
BURST_CUTS = (5, 9)
BURST_GAP = (0.2, 0.4)
CUTS_PER_SEC = (0.6, 0.8)
LUFS = -14.0
ASPECTS = {"16:9": (1920, 1080), "9:16": (1080, 1920), "1:1": (1080, 1080)}


class Missing(Exception):
    pass


# Check id -> criterion id in video-lab-tools/docs/PROCESS_SPEC.md (C<mission>.<n>).
CID = {
    "brief": {"name": "C1.1", "purpose": "C1.1", "map_row": "C1.1", "duration": "C1.2", "aspect": "C1.3",
              "commercial": "C1.4", "tools": "C1.5", "colors": "C1.6", "pace": "C1.7"},
    "storyboard": {"coverage": "C2.1", "normal_avg": "C2.2", "burst_pos": "C2.3", "burst_cuts": "C2.4",
                   "burst_gap": "C2.5", "words": "C2.6", "burst_count": "C2.7"},
    "music": {"length": "C3.1", "tempo": "C3.2", "loudness": "C3.3", "grid": "C3.4", "license": "C3.5", "seams": "C3.6"},
    "draft": {"fps": "C4.1", "length": "C4.2", "cuts_per_sec": "C4.3", "burst": "C4.4", "audio": "C4.5", "plan_match": "C4.6", "beat_sync": "C4.7"},
    "final": {"fps": "C5.1", "length": "C5.2", "cuts_per_sec": "C5.3", "burst": "C5.3", "audio": "C5.4",
              "loudness": "C5.4", "size": "C5.5", "proposal": "C5.6", "codec": "C5.7"},
}


def chk(cid: str, label: str, value, target: str, ok: bool) -> dict:
    return {"id": cid, "label": label, "value": value, "target": target, "pass": bool(ok)}


def load_json(p: Path) -> dict:
    if not p.is_file():
        raise Missing(f"없음: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def probe(p: Path) -> dict:
    if not p.is_file():
        raise Missing(f"없음: {p}")
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration:stream=codec_type,width,height,avg_frame_rate",
                        "-of", "json", str(p)], capture_output=True, text=True, check=True)
    d = json.loads(r.stdout)
    v = next((s for s in d.get("streams", []) if s.get("codec_type") == "video"), {})
    num, _, den = (v.get("avg_frame_rate") or "0/1").partition("/")
    fps = float(num) / float(den or 1) if float(den or 1) else 0.0
    return {"duration": round(float(d["format"].get("duration", 0)), 3), "width": v.get("width"),
            "height": v.get("height"), "fps": round(fps, 2),
            "audio": any(s.get("codec_type") == "audio" for s in d.get("streams", []))}


def loudness(p: Path) -> float | None:
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(p), "-af",
                        "loudnorm=I=-14:TP=-1:LRA=9:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    m = re.search(r'"input_i"\s*:\s*"(-?[\d.]+|-inf)"', r.stderr)
    return None if not m or m.group(1) == "-inf" else float(m.group(1))


def within(x, lo, hi) -> bool:
    return x is not None and lo <= x <= hi


# ---------- missions ----------

NA = "해당 없음 (explainer)"
MAX_SHORT, MAX_LONG = 28, 60
EXPLAINER_SCENE = (2.0, 5.0)
FRAME_TOL = 0.05   # about 1.5 frames at 30 fps
PLAN_TOL = 0.1


def pace_of(b: dict) -> str:
    return "explainer" if b.get("pace") == "explainer" else "fast"


def na(cid_id: str, label: str, target: str) -> dict:
    return chk(cid_id, label, NA, target, True)


def m_brief(proj: Path) -> list[dict]:
    b = load_json(proj / "brief.json")
    dur = b.get("duration_s")
    cap = MAX_LONG if b.get("long_music") is True else MAX_SHORT
    colors = [c for c in (b.get("colors") or []) if re.fullmatch(r"#?[0-9a-fA-F]{6}", str(c))]
    cap_note = " (long_music)" if cap == MAX_LONG else " (28 초과는 long_music)"
    return [
        chk("name", "이름", b.get("name"), "있음", bool(b.get("name"))),
        chk("purpose", "목적", (b.get("purpose") or "")[:60], "있음", bool(b.get("purpose"))),
        chk("map_row", "지도 줄", b.get("map_row"), "있음", bool(b.get("map_row"))),
        chk("duration", "길이(초)", dur, f"5~{cap}{cap_note}", isinstance(dur, (int, float)) and 5 <= dur <= cap),
        chk("aspect", "비율", b.get("aspect"), "16:9 · 9:16 · 1:1", b.get("aspect") in ASPECTS),
        chk("commercial", "상업 여부", b.get("commercial"), "true/false", isinstance(b.get("commercial"), bool)),
        chk("tools", "템플릿/스킬", b.get("templates"), "1개 이상", bool(b.get("templates"))),
        chk("colors", "브랜드 색", colors, "hex 2개 이상", len(colors) >= 2),
        chk("pace", "빠르기", b.get("pace"), "fast / explainer", b.get("pace") in ("fast", "explainer")),
    ]


def burst_groups(scenes: list[dict]) -> list[list[dict]]:
    groups, cur = [], []
    for s in scenes:
        if s.get("part") == "burst" and (not cur or abs(s["start_s"] - cur[-1]["end_s"]) <= 0.05):
            cur.append(s)
            continue
        if cur:
            groups.append(cur)
        cur = [s] if s.get("part") == "burst" else []
    if cur:
        groups.append(cur)
    return groups


def m_storyboard(proj: Path) -> list[dict]:
    b = load_json(proj / "brief.json")
    sb = load_json(proj / "storyboard.json")
    dur = float(b.get("duration_s") or 0)
    pace = pace_of(b)
    sc = sorted(sb.get("scenes", []), key=lambda s: s["start_s"])
    if not sc:
        raise Missing("storyboard.json에 scenes가 없음")
    gaps = [round(n["start_s"] - p["end_s"], 3) for p, n in zip(sc, sc[1:])]
    covered = abs(sc[0]["start_s"]) <= 0.1 and abs(sc[-1]["end_s"] - dur) <= 0.1 and all(abs(g) <= 0.1 for g in gaps)
    normal = [s["end_s"] - s["start_s"] for s in sc if s.get("part", "normal") == "normal"]
    avg_n = round(sum(normal) / len(normal), 2) if normal else None
    rng = NORMAL_SCENE if pace == "fast" else EXPLAINER_SCENE
    words = max((len(str(s.get("text", "")).split()) for s in sc), default=0)
    out = [
        chk("coverage", "타임라인 빈틈", f"{sc[0]['start_s']}~{sc[-1]['end_s']}s", f"0~{dur}s, 빈틈 ≤0.1s", covered),
        chk("normal_avg", "보통 장면 평균(초)", avg_n, f"{rng[0]}~{rng[1]} ({pace})", within(avg_n, *rng)),
        chk("words", "장면당 최대 단어", words, "≤5", words <= 5),
    ]
    if pace == "explainer":
        return out + [na("burst_count", "몰아치기 개수", "fast만"), na("burst_pos", "몰아치기 위치", "fast만"),
                      na("burst_cuts", "몰아치기 컷 수", "fast만"), na("burst_gap", "몰아치기 간격", "fast만")]
    groups = burst_groups(sc)
    want = max(1, round(dur / 15))
    last_pos = round(groups[-1][0]["start_s"] / dur, 3) if groups and dur else None
    sizes = [len(g) for g in groups]
    lens = [round(s["end_s"] - s["start_s"], 3) for g in groups for s in g]
    return out + [
        chk("burst_count", "몰아치기 개수", len(groups), f"{want} (15초당 1)", len(groups) == want),
        chk("burst_pos", "마지막 몰아치기 위치", last_pos, f"{BURST_POS[0]}~{BURST_POS[1]}", within(last_pos, *BURST_POS)),
        chk("burst_cuts", "몰아치기마다 컷 수", sizes, f"각 {BURST_CUTS[0]}~{BURST_CUTS[1]}",
            bool(sizes) and all(BURST_CUTS[0] <= n <= BURST_CUTS[1] for n in sizes)),
        chk("burst_gap", "몰아치기 간격(초)", lens, f"각 {BURST_GAP[0]}~{BURST_GAP[1]}",
            bool(lens) and all(BURST_GAP[0] - 0.01 <= x <= BURST_GAP[1] + 0.01 for x in lens)),
    ]


def seam_levels(wav: Path, seams: list[float]) -> list[float]:
    """dB difference between the 0.5 s before and after each seam (RMS from ffmpeg astats)."""
    diffs = []
    for t in seams:
        lv = []
        for start in (max(0.0, t - 0.5), t):
            r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-ss", f"{start:.3f}", "-t", "0.5", "-i", str(wav),
                                "-af", "astats=metadata=0", "-f", "null", "-"],
                               capture_output=True, text=True, encoding="utf-8", errors="replace")
            m = re.findall(r"RMS level dB:\s*(-?[\d.]+|-inf)", r.stderr)
            lv.append(float(m[-1]) if m and m[-1] != "-inf" else -90.0)
        diffs.append(round(abs(lv[0] - lv[1]), 2))
    return diffs


def m_music(proj: Path) -> list[dict]:
    b = load_json(proj / "brief.json")
    bgm = proj / "assets" / "bgm"
    rep = load_json(bgm / "report.json")
    grid = bgm / "bgm.grid.json"
    info = probe(bgm / "bgm.wav")
    dur = float(b.get("duration_s") or 0)
    target = float(rep.get("target_bpm") or 0)
    ratio = float(rep.get("stretch_ratio") or 1.0)
    got = round(float(rep.get("detected_bpm") or 0) * ratio, 2)
    lu = loudness(bgm / "bgm.wav")
    nc = "NC" in str(rep.get("license", ""))
    out = [
        chk("length", "길이(초)", info["duration"], f"{dur} ±0.05", abs(info["duration"] - dur) <= 0.05),
        chk("tempo", "BPM", got, f"{target} ±2", abs(got - target) <= 2 and 0.8 <= ratio <= 1.25),
        chk("loudness", "음량(LUFS)", lu, f"{LUFS} ±1", lu is not None and abs(lu - LUFS) <= 1.0),
        chk("grid", "박자 그리드", grid.is_file(), "있음", grid.is_file()),
        chk("license", "라이선스", rep.get("license", "자체/구매"), "상업이면 NC 불가", not (b.get("commercial") is True and nc)),
    ]
    seams = [float(x) for x in rep.get("seams_s", [])]
    if dur <= MAX_SHORT and not seams:
        return out + [chk("seams", "이음새", "해당 없음 (28초 이하)", "긴 음악만", True)]
    inside = [t for t in seams if 0.5 < t < info["duration"] - 0.5]
    want = int(rep.get("chunks", 1)) - 1
    diffs = seam_levels(bgm / "bgm.wav", inside)
    return out + [chk("seams", "이음새 (개수 · 음량 차 dB)", {"count": len(inside), "db": diffs},
                      f"{max(want, 0)}개 이하 · 각 ≤3dB", len(inside) <= max(want, 0) and all(d <= 3.0 for d in diffs))]


def rhythm(video: Path, dur: float) -> tuple[float, dict | None, list[float]]:
    import sample_speed as ss  # same measuring method as the template sampling
    m = ss.measure(ss.scene_scores(video), dur)
    bs = ss.bursts(m["cut_times"])
    return m["cuts_per_sec"], (bs[-1] if bs else None), m["cut_times"]


def ratio_near(points: list[float], ref: list[float], tol: float) -> float | None:
    if not points or not ref:
        return None
    return round(sum(1 for p in points if min(abs(p - r) for r in ref) <= tol) / len(points), 3)


def m_render(proj: Path, name: str, fps_target: int) -> list[dict]:
    b = load_json(proj / "brief.json")
    dur = float(b.get("duration_s") or 0)
    pace = pace_of(b)
    info = probe(proj / name)
    cps, burst, cuts = rhythm(proj / name, info["duration"])
    b_pos = round(burst["start"] / info["duration"], 3) if burst else None
    out = [
        chk("fps", "fps", info["fps"], str(fps_target), abs(info["fps"] - fps_target) <= 0.5),
        chk("length", "길이(초)", info["duration"], f"{dur} ±0.15", abs(info["duration"] - dur) <= 0.15),
        chk("audio", "소리", info["audio"], "있음", info["audio"]),
    ]
    if pace == "fast":
        out += [chk("cuts_per_sec", "초당 컷", cps, f"{CUTS_PER_SEC[0]}~{CUTS_PER_SEC[1]}", within(cps, *CUTS_PER_SEC)),
                chk("burst", "잰 몰아치기 위치 (마지막)", b_pos, f"{BURST_POS[0]}~{BURST_POS[1]}", within(b_pos, *BURST_POS))]
    else:
        out += [na("cuts_per_sec", "초당 컷", "fast만"), na("burst", "잰 몰아치기 위치", "fast만")]
    if fps_target == 30:
        sbp = proj / "storyboard.json"
        plan = sorted({round(s["start_s"], 3) for s in load_json(sbp).get("scenes", []) if s["start_s"] > 0.05}) if sbp.is_file() else []
        hit = ratio_near(plan, cuts, PLAN_TOL)
        gp = proj / "assets" / "bgm" / "bgm.grid.json"
        eighths = load_json(gp).get("eighths", []) if gp.is_file() else []
        beat = ratio_near(cuts, eighths, FRAME_TOL)
        out += [chk("plan_match", "계획대로 잘림", hit, f"≥0.8 (±{PLAN_TOL}s)", hit is not None and hit >= 0.8),
                chk("beat_sync", "박자에 컷", beat, f"≥0.8 (±{FRAME_TOL}s)", beat is not None and beat >= 0.8)]
    if fps_target == 60:
        w, h = ASPECTS.get(b.get("aspect"), (None, None))
        lu = loudness(proj / name)
        props = (LAB / "index" / "proposals.md").read_text(encoding="utf-8") if (LAB / "index" / "proposals.md").is_file() else ""
        r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=codec_name,pix_fmt",
                            "-of", "csv=p=0", str(proj / name)], capture_output=True, text=True)
        codec = r.stdout.strip()
        out += [
            chk("size", "해상도", f"{info['width']}x{info['height']}", f"{w}x{h}", (info["width"], info["height"]) == (w, h)),
            chk("loudness", "음량(LUFS)", lu, f"{LUFS} ±1.5", lu is not None and abs(lu - LUFS) <= 1.5),
            chk("proposal", "제안 기록", proj.name in props, "proposals.md에 프로젝트 이름", proj.name in props),
            chk("codec", "업로드 형식", codec, "h264,yuv420p", codec == "h264,yuv420p"),
        ]
    return out


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mission", choices=["brief", "storyboard", "music", "draft", "final"])
    ap.add_argument("--project", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    proj = LAB / "projects" / a.project
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    dest = out / f"video-mission-{a.mission}-check.json"
    try:
        checks = {"brief": lambda: m_brief(proj), "storyboard": lambda: m_storyboard(proj),
                  "music": lambda: m_music(proj), "draft": lambda: m_render(proj, "draft.mp4", 30),
                  "final": lambda: m_render(proj, "final.mp4", 60)}[a.mission]()
        code = 0 if all(c["pass"] for c in checks) else 1
    except Missing as e:
        checks, code = [chk("input", "입력 파일", str(e), "있어야 함", False)], 2
    for c in checks:
        c["cid"] = CID[a.mission].get(c["id"], "-")
    doc = {"mission": a.mission, "project": a.project, "measured_at": datetime.now().isoformat(timespec="seconds"),
           "checks": checks, "pass": code == 0}
    dest.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    # Readable twin: the AI-DLC stage declares the artifact `video-mission-<m>-check`, resolved as .md.
    rows = "\n".join(f"| {c['cid']} | {c['label']} | {c['value']} | {c['target']} | {'✅' if c['pass'] else '❌'} |" for c in checks)
    dest.with_suffix(".md").write_text(
        f"# {a.mission} 측정 결과\n\n측정 {doc['measured_at']} · 프로젝트 `{a.project}` · 원본 `{dest.name}`\n\n"
        f"| C | 항목 | 값 | 기준 | 통과 |\n|---|---|---|---|---|\n{rows}\n\n**{'PASS' if code == 0 else 'FAIL'}**\n",
        encoding="utf-8")
    for c in checks:
        print(f"{'✅' if c['pass'] else '❌'} {c['cid']} {c['label']}: {c['value']} (기준 {c['target']})")
    print(f"→ {dest}  [{'PASS' if code == 0 else 'FAIL'}]")
    refresh_dashboard(dest)
    return code


def refresh_dashboard(dest: Path) -> None:
    """Rebuild the static video-mission dashboard of the AI-DLC project that holds this record
    (the folder above `aidlc/` with scripts/mission_dashboard.py). Best effort: never fails the check."""
    import subprocess
    for up in dest.resolve().parents:
        if up.name == "aidlc":
            script = up.parent / "scripts" / "mission_dashboard.py"
            if script.is_file():
                try:
                    subprocess.run([sys.executable, "-I", str(script)], cwd=up.parent, timeout=60,
                                   capture_output=True, check=False)
                    print(f"  대시보드 갱신: {up.parent / 'dashboard' / 'index.html'}")
                except (OSError, subprocess.SubprocessError) as e:
                    print(f"  (대시보드 갱신 건너뜀: {e})")
            return


if __name__ == "__main__":
    raise SystemExit(main())
