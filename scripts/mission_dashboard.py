"""Card dashboard for video-mission AI-DLC runs (spec: docs/PROCESS_SPEC.md 7장).

  python scripts/mission_dashboard.py            # real runs under aidlc/spaces/*/intents/
  python scripts/mission_dashboard.py --demo     # sample data, clearly labelled
  python scripts/mission_dashboard.py --json     # print data only

Writes dashboard/index.html (cards, light/dark via theme vars with fallbacks),
dashboard/data.json, and DASHBOARD.md (same cards in Markdown, for the
AIDLC-VIEWER panel and plain editors). Read-only on AI-DLC records.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import quote, unquote

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "dashboard"
MISSIONS = [("brief", "M1", "기획"), ("storyboard", "M2", "스토리보드"), ("music", "M3", "음악"),
            ("draft", "M4", "시험 렌더"), ("final", "M5", "최종")]
STATE = {" ": ("대기", "muted"), "-": ("진행", "info"), "?": ("승인 대기", "warn"),
         "R": ("수정 중", "warn"), "x": ("완료", "ok"), "S": ("건너뜀", "muted")}
ROW = re.compile(r"^- \[(.)\] (video-mission-[a-z]+)\b", re.M)


def read_state(record: Path) -> dict[str, str]:
    f = record / "aidlc-state.md"
    return {m.group(2): m.group(1) for m in ROW.finditer(f.read_text(encoding="utf-8"))} if f.is_file() else {}


def first_line(md: Path, heading: str) -> str:
    if not md.is_file():
        return ""
    m = re.search(rf"^## {heading}\s*\n(.*?)(?=^## |\Z)", md.read_text(encoding="utf-8"), re.M | re.S)
    if not m:
        return ""
    lines = [l.strip() for l in m.group(1).splitlines() if l.strip() and not l.strip().startswith("<!--")]
    return lines[0][:160] if lines else ""


SPEC = {m["slug"]: m for m in json.loads((ROOT / "docs" / "missions.json").read_text(encoding="utf-8"))["missions"]}
REQ_LINE = re.compile(r"^- \[( |x|X)\] (F\d+\.\d+)", re.M)


def requirements_view(slug: str, summary: Path | None, checks: list[dict]) -> dict:
    """F list (done flags from the summary's ## Requirements) + C list (status from the check JSON)."""
    m = SPEC[slug]
    done = {}
    if summary and summary.is_file():
        sec = re.search(r"^## Requirements\s*\n(.*?)(?=^## |\Z)", summary.read_text(encoding="utf-8"), re.M | re.S)
        done = {fid: mark.lower() == "x" for mark, fid in REQ_LINE.findall(sec.group(1) if sec else "")}
    by_cid: dict[str, list[bool]] = {}
    for c in checks:
        by_cid.setdefault(c.get("cid", "-"), []).append(c.get("pass") is True)
    reqs = [{"id": r["id"], "text": r["text"], "done": done.get(r["id"])} for r in m["requirements"]]
    crit = [{"cid": c["cid"], "text": c["text"], "target": c["target"],
             "pass": (all(by_cid[c["cid"]]) if c["cid"] in by_cid else None)} for c in m["criteria"]]
    return {"requirements": reqs, "criteria": crit, "goal": m["goal"], "weight": m["weight"],
            "req_done": sum(1 for r in reqs if r["done"]), "req_total": len(reqs)}


def mission_card(record: Path, slug: str, code: str, label: str, marks: dict[str, str]) -> dict:
    stage = f"video-mission-{slug}"
    check = next(iter(sorted(record.rglob(f"{stage}-check.json"))), None)
    summary = next(iter(sorted(record.rglob(f"{stage}.md"))), None)
    mark = marks.get(stage, " ")
    card = {"code": code, "mission": slug, "label": label, "state": STATE.get(mark, STATE[" "])[0],
            "state_tone": STATE.get(mark, STATE[" "])[1], "verdict": "NOT MEASURED", "passed": 0, "total": 0,
            "failed": [], "result": "", "measured_at": "", "summary": str(summary) if summary else ""}
    cs: list[dict] = []
    if check:
        d = json.loads(check.read_text(encoding="utf-8"))
        cs = d.get("checks", [])
        card.update(passed=sum(1 for c in cs if c.get("pass") is True), total=len(cs),
                    failed=[f"{c.get('cid', '')} {c.get('label')}: {c.get('value')} (기준 {c.get('target')})" for c in cs if c.get("pass") is not True],
                    measured_at=d.get("measured_at", ""))
        card["verdict"] = "PASS" if cs and card["passed"] == len(cs) else "FAIL"
        if card["verdict"] == "FAIL" and mark == "x":
            card["verdict"] = "OVERRIDE"
    if summary:
        card["result"] = first_line(summary, "Result")
    card.update(requirements_view(slug, summary, cs))
    return card


PROJECTS = ROOT.parent / "video-lab" / "projects"
MEDIA = ("final.mp4", "draft.mp4", "snapshots/contact-sheet.jpg", "comp/snapshots/contact-sheet.jpg")
FIELD = lambda name: re.compile(rf"^- \*\*{re.escape(name)}\*\*:\s*(.+)$", re.M)  # noqa: E731


def state_field(record: Path, name: str) -> str:
    f = record / "aidlc-state.md"
    m = FIELD(name).search(f.read_text(encoding="utf-8")) if f.is_file() else None
    return m.group(1).strip() if m else ""


def run_info(record: Path, cards: list[dict]) -> dict:
    """Per-video header: which project, where it stands, its brief and its media files."""
    project = ""
    for chk in sorted(record.rglob("video-mission-*-check.json")):
        project = json.loads(chk.read_text(encoding="utf-8")).get("project", "") or project
        if project:
            break
    title = re.sub(r"^video-mission-video\s+", "", state_field(record, "Project")) or record.name
    done = sum(1 for c in cards if c["state"] == "완료")
    parked = state_field(record, "Parked At Stage")
    nxt = next((c for c in cards if c["state"] != "완료"), None)
    if done == len(cards):
        status, tone = "완료", "ok"
    elif parked:
        status, tone = f"멈춤 · {nxt['code'] if nxt else ''} {nxt['label'] if nxt else parked}", "muted"
    else:
        status, tone = f"진행 중 · {nxt['code']} {nxt['label']}" if nxt else "진행 중", "info"
    m = re.match(r"(\d{2})(\d{2})(\d{2})-", record.name)
    pdir = PROJECTS / project if project else None
    brief = {}
    if pdir and (pdir / "brief.json").is_file():
        b = json.loads((pdir / "brief.json").read_text(encoding="utf-8"))
        brief = {k: b.get(k) for k in ("duration_s", "aspect", "pace", "commercial", "purpose", "colors")}
    media = {k: f"{project}/{k}" for k in MEDIA if pdir and (pdir / k).is_file()}
    return {"project": project, "title": title, "status": status, "status_tone": tone, "done": done,
            "started": f"20{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else "", "path": str(pdir) if pdir else "",
            "brief": brief, "media": media}


def collect() -> list[dict]:
    runs = []
    for record in sorted(ROOT.glob("aidlc/spaces/*/intents/*/")):
        if record.name.startswith("."):
            continue
        marks = read_state(record)
        if not any(k.startswith("video-mission-") for k in marks) and not any(record.rglob("video-mission-*-check.json")):
            continue
        cards = [mission_card(record, *m, marks) for m in MISSIONS]
        runs.append({"intent": record.name, "space": record.parent.parent.name, "cards": cards, **run_info(record, cards)})
    return runs


def stamp() -> str:
    """Changes whenever a record, a project's media or this script changes - the page polls it."""
    files = [Path(__file__)] + [p for p in ROOT.glob("aidlc/spaces/*/intents/**/*") if p.is_file()]
    for r in collect_projects():
        files += [r / k for k in ("brief.json", *MEDIA)]
    return str(int(max((f.stat().st_mtime for f in files if f.is_file()), default=0)))


def collect_projects() -> list[Path]:
    names = set()
    for chk in ROOT.glob("aidlc/spaces/*/intents/*/**/video-mission-*-check.json"):
        names.add(json.loads(chk.read_text(encoding="utf-8")).get("project", ""))
    return [PROJECTS / n for n in sorted(names) if n]


def demo() -> list[dict]:
    def c(code, slug, label, state, tone, verdict, passed, total, failed, result):
        return {"code": code, "mission": slug, "label": label, "state": state, "state_tone": tone, "verdict": verdict,
                "passed": passed, "total": total, "failed": failed, "result": result, "measured_at": "2026-11-20T11:00:00", "summary": ""}
    _demo_runs = [{"intent": "예시-acme-notes (가짜 데이터)", "space": "default", "cards": [
        c("M1", "brief", "기획", "완료", "ok", "PASS", 7, 7, [], "15초 · 16:9 · 비상업 · 지도: 빠른 출시 영상 · 템플릿 18"),
        c("M2", "storyboard", "스토리보드", "완료", "ok", "PASS", 6, 6, [], "장면 11개 · 몰아치기 56% 지점 7컷 0.25초"),
        c("M3", "music", "음악", "완료", "ok", "PASS", 5, 5, [], "minimal-techno 128 BPM · 15.0초 · -14.4 LUFS"),
        c("M4", "draft", "시험 렌더", "승인 대기", "warn", "FAIL", 4, 5, ["C4.5 소리: False (기준 있음)"], "draft.mp4 30fps · 초당 컷 0.8 · 몰아치기 60%"),
        c("M5", "final", "최종", "대기", "muted", "NOT MEASURED", 0, 0, [], ""),
    ]}]
    runs = _demo_runs
    for card in runs[0]["cards"]:
        m = SPEC[card["mission"]]
        st = card["verdict"]
        done = {"PASS": True, "FAIL": True, "NOT MEASURED": None}[st]
        reqs = [{"id": r["id"], "text": r["text"], "done": done} for r in m["requirements"]]
        crit = [{"cid": c["cid"], "text": c["text"], "target": c["target"],
                 "pass": None if st == "NOT MEASURED" else not (st == "FAIL" and c["cid"] == "C4.5")} for c in m["criteria"]]
        card.update(requirements=reqs, criteria=crit, goal=m["goal"], weight=m["weight"],
                    req_done=sum(1 for r in reqs if r["done"]), req_total=len(reqs))
    return runs


TONE = {"PASS": "ok", "FAIL": "danger", "OVERRIDE": "warn", "NOT MEASURED": "muted"}
FALLBACK = {"bg": "#f7f7f8", "text": "#1d1d1f", "card": "#ffffff", "card-fg": "#1d1d1f", "border": "#dcdce0",
            "muted": "#6e6e73", "ok": "#1f8a4c", "warn": "#b26a00", "danger": "#c62828", "info": "#1f6feb",
            "ok-subtle": "#e7f5ec", "warn-subtle": "#fff4e0", "danger-subtle": "#fdeaea", "accent-subtle": "#eaf1fe"}


def v(name: str) -> str:
    return f"var(--{name},{FALLBACK.get(name, '#888')})"


def render_html(runs: list[dict], is_demo: bool, media_base: str = "file", stamp_value: str = "") -> str:
    def esc(x) -> str:
        return html.escape(str(x))

    def card(c: dict) -> str:
        tone = TONE[c["verdict"]]
        pct = int(100 * c["passed"] / c["total"]) if c["total"] else 0
        fails = "".join(f'<li style="color:{v("danger")}">{esc(f)}</li>' for f in c["failed"])
        return f"""<div style="background:{v('card')};color:{v('card-fg')};border:1px solid {v('border')};border-top:4px solid {v(tone)};border-radius:12px;padding:14px;display:flex;flex-direction:column;gap:8px;min-height:190px">
  <div style="display:flex;justify-content:space-between;align-items:center"><span style="font-weight:700">{esc(c['code'])} {esc(c['label'])}</span>
  <span style="font-size:12px;padding:2px 8px;border-radius:999px;background:{v(c['state_tone'] + '-subtle' if c['state_tone'] in ('ok', 'warn') else 'accent-subtle')};color:{v(c['state_tone'])}">{esc(c['state'])}</span></div>
  <div style="font-size:22px;font-weight:800;color:{v(tone)}">{esc(c['verdict'])}</div>
  <div style="font-size:12px;color:{v('muted')}">판정 {c['passed']}/{c['total']}</div>
  <div style="height:6px;background:{v('border')};border-radius:3px;overflow:hidden"><div style="width:{pct}%;height:100%;background:{v(tone)}"></div></div>
  <div style="font-size:13px">{esc(c['result']) or f'<span style="color:{v("muted")}">요약 없음</span>'}</div>
  {f'<ul style="margin:0;padding-left:18px;font-size:12px">{fails}</ul>' if fails else ''}
  {reqbox(c)}
</div>"""

    def mark(x) -> str:
        return {True: "✅", False: "❌", None: "⚪"}[x]

    def reqbox(c: dict) -> str:
        f_rows = "".join(f'<li>{mark(r["done"])} <b>{esc(r["id"])}</b> {esc(r["text"])}</li>' for r in c["requirements"])
        c_rows = "".join(f'<li>{mark(x["pass"])} <b>{esc(x["cid"])}</b> {esc(x["text"])} <span style="color:{v("muted")}">· {esc(x["target"])}</span></li>' for x in c["criteria"])
        return f"""<details style="font-size:12px;border-top:1px solid {v('border')};padding-top:6px"><summary style="cursor:pointer">요구사항 · 기능 {c['req_done']}/{c['req_total']} · 기준 {sum(1 for x in c['criteria'] if x['pass'])}/{len(c['criteria'])}</summary>
<div style="color:{v('muted')};margin:4px 0">{esc(c['goal'])} · {esc(c['weight'])}</div>
<div style="font-weight:700;margin-top:4px">해야 할 일</div><ul style="margin:2px 0;padding-left:4px;list-style:none">{f_rows}</ul>
<div style="font-weight:700;margin-top:4px">통과 기준</div><ul style="margin:2px 0;padding-left:4px;list-style:none">{c_rows}</ul></details>"""

    def media_url(rel: str) -> str:
        if media_base == "http":
            return "/media/" + "/".join(quote(x) for x in rel.split("/"))
        return (PROJECTS / rel).as_uri()

    def chips(r: dict) -> str:
        b = r.get("brief") or {}
        items = []
        if b.get("duration_s"):
            items.append(f"{b['duration_s']}초")
        items += [str(b[k]) for k in ("aspect", "pace") if b.get(k)]
        if "commercial" in b:
            items.append("상업" if b["commercial"] else "비상업")
        sw = "".join(f'<span title="{esc(c)}" style="display:inline-block;width:14px;height:14px;border-radius:4px;background:{esc(c)};border:1px solid {v("border")};vertical-align:middle"></span>'
                     for c in (b.get("colors") or [])[:5])
        pills = " ".join(f'<span style="font-size:12px;padding:2px 8px;border-radius:999px;background:{v("accent-subtle")};color:{v("info")}">{esc(x)}</span>' for x in items)
        return pills + (" " + sw if sw else "")

    def media_panel(r: dict) -> str:
        m = r.get("media") or {}
        vid = m.get("final.mp4") or m.get("draft.mp4")
        sheet = m.get("snapshots/contact-sheet.jpg") or m.get("comp/snapshots/contact-sheet.jpg")
        parts = []
        if vid:
            label = "최종본 final.mp4" if m.get("final.mp4") else "초안 draft.mp4"
            parts.append(f'<div style="flex:1 1 420px"><div style="font-size:12px;color:{v("muted")};margin-bottom:4px">{label}</div>'
                         f'<video src="{media_url(vid)}" controls preload="metadata" style="width:100%;border-radius:10px;background:#000"></video></div>')
        if sheet:
            parts.append(f'<div style="flex:1 1 420px"><div style="font-size:12px;color:{v("muted")};margin-bottom:4px">장면 모음</div>'
                         f'<img src="{media_url(sheet)}" alt="contact sheet" style="width:100%;border-radius:10px"></div>')
        return f'<div style="display:flex;flex-wrap:wrap;gap:12px;margin:12px 0">{"".join(parts)}</div>' if parts else ""

    def dots(r: dict) -> str:
        out = []
        for c in r["cards"]:
            col = v(TONE[c["verdict"]]) if c["verdict"] != "NOT MEASURED" else v("border")
            out.append(f'<span title="{esc(c["code"])} {esc(c["label"])} · {esc(c["state"])} · {esc(c["verdict"])}" '
                       f'style="display:inline-block;width:22px;height:8px;border-radius:4px;margin-right:3px;background:{col}"></span>')
        return "".join(out)

    tabs, panels, rows = [], [], []
    for r in runs:
        tid = esc(r["intent"])
        name = r.get("project") or r["intent"]
        tone = r.get("status_tone", "muted")
        status = esc(r.get("status", ""))
        tabs.append(f'<button class="tab" data-tab="{tid}"><span style="display:inline-block;width:8px;height:8px;border-radius:4px;background:{v(tone)};margin-right:6px"></span>{esc(name)}</button>')
        rows.append(f'<tr data-go="{tid}" style="cursor:pointer;border-top:1px solid {v("border")}">'
                    f'<td style="padding:8px"><b>{esc(name)}</b><div style="font-size:12px;color:{v("muted")}">{esc(r.get("title", ""))}</div></td>'
                    f'<td style="padding:8px;font-size:13px">{esc(r.get("started", ""))}</td>'
                    f'<td style="padding:8px;font-size:13px;color:{v(tone)}">{status}</td>'
                    f'<td style="padding:8px">{dots(r)} <span style="font-size:12px;color:{v("muted")}">{r.get("done", 0)}/5</span></td>'
                    f'<td style="padding:8px">{chips(r)}</td></tr>')
        path = (f'<div style="font-size:12px;color:{v("muted")}">프로젝트 <code>{esc(r["path"])}</code> · 기록 '
                f'<code>aidlc/spaces/{esc(r["space"])}/intents/{tid}/</code></div>') if r.get("path") else ""
        panels.append(f"""<section class="panel" data-panel="{tid}" hidden>
<div style="display:flex;gap:10px;align-items:baseline;flex-wrap:wrap"><h2 style="margin:0;font-size:18px">{esc(name)}</h2>
<span style="color:{v(tone)};font-size:13px">{status}</span><span style="color:{v('muted')};font-size:13px">{r.get('done', 0)}/5 미션 완료 · 시작 {esc(r.get('started', ''))}</span></div>
<div style="margin:4px 0 6px">{esc(r.get('title', ''))}</div><div style="margin-bottom:4px">{chips(r)}</div>{path}
{media_panel(r)}
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin-top:12px">{''.join(card(c) for c in r['cards'])}</div></section>""")
    if runs:
        th = f'style="padding:8px"'
        overview = (f'<section class="panel" data-panel="all" hidden><table style="width:100%;border-collapse:collapse;background:{v("card")};color:{v("card-fg")};border:1px solid {v("border")}">'
                    f'<thead><tr style="text-align:left;font-size:12px;color:{v("muted")}"><th {th}>영상</th><th {th}>시작</th><th {th}>상태</th><th {th}>M1→M5</th><th {th}>조건</th></tr></thead>'
                    f'<tbody>{"".join(rows)}</tbody></table><div style="font-size:12px;color:{v("muted")};margin-top:6px">줄을 누르면 그 영상 탭으로 갑니다.</div></section>')
        nav = (f'<nav role="tablist" style="display:flex;gap:6px;flex-wrap:wrap;border-bottom:1px solid {v("border")};margin-bottom:14px">'
               f'<button class="tab" data-tab="all">전체 ({len(runs)})</button>{"".join(tabs)}</nav>')
        body = nav + overview + "".join(panels)
    else:
        body = f'<p style="color:{v("muted")}">아직 video-mission 실행이 없습니다. <code>/aidlc video-mission-video …</code>로 시작하세요.</p>'
    default = esc(runs[-1]["intent"]) if runs else "all"
    banner = f'<div style="background:{v("warn-subtle")};color:{v("warn")};padding:8px 12px;border-radius:8px;margin-bottom:14px">예시 데이터입니다 (실제 실행 아님)</div>' if is_demo else ""
    live = "실시간 · 기록이 바뀌면 자동 새로고침" if media_base == "http" else "정적 파일 · <code>--serve</code>로 열면 자동 갱신"
    script = SCRIPT.replace("__DEFAULT__", default).replace("__STAMP__", esc(stamp_value))
    style = (f"<style>.tab{{font:inherit;font-size:14px;padding:8px 14px;border:1px solid transparent;border-bottom:none;border-radius:10px 10px 0 0;"
             f"background:none;color:{v('muted')};cursor:pointer;margin-bottom:-1px}}"
             f".tab[aria-selected=true]{{background:{v('card')};color:{v('text')};border-color:{v('border')};font-weight:700}}"
             f"tbody tr:hover{{background:{v('accent-subtle')}}}</style>")
    return f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>video-mission 대시보드</title>
<meta name="viewport" content="width=device-width,initial-scale=1">{style}</head>
<body style="margin:0;padding:18px;background:{v('bg')};color:{v('text')};font-family:system-ui,'Malgun Gothic',sans-serif">
<h1 style="margin:0 0 4px;font-size:20px">영상 미션 대시보드</h1>
<div style="color:{v('muted')};font-size:12px;margin-bottom:14px">생성 {datetime.now():%Y-%m-%d %H:%M} · {live} · 기준 docs/PROCESS_SPEC.md</div>
{banner}{body}{script}</body></html>"""


# Tabs keep their place in the URL hash, so a reload (manual or automatic) lands on the same video.
# Under --serve the page polls /stamp every 5 s and reloads when a record or media file changed
# (never while a video is playing).
SCRIPT = """<script>
(function () {
  var tabs = [].slice.call(document.querySelectorAll('.tab'));
  var panels = [].slice.call(document.querySelectorAll('.panel'));
  function show(id) {
    if (!panels.some(function (p) { return p.dataset.panel === id; })) id = '__DEFAULT__';
    panels.forEach(function (p) { p.hidden = p.dataset.panel !== id; });
    tabs.forEach(function (t) { t.setAttribute('aria-selected', t.dataset.tab === id); });
    if (decodeURIComponent(location.hash.slice(1)) !== id) history.replaceState(null, '', '#' + id);
  }
  tabs.forEach(function (t) { t.onclick = function () { show(t.dataset.tab); }; });
  [].slice.call(document.querySelectorAll('[data-go]')).forEach(function (r) { r.onclick = function () { show(r.dataset.go); }; });
  show(decodeURIComponent(location.hash.slice(1)) || '__DEFAULT__');
  var st = '__STAMP__';
  if (location.protocol.indexOf('http') === 0) setInterval(function () {
    if ([].slice.call(document.querySelectorAll('video')).some(function (x) { return !x.paused; })) return;
    fetch('/stamp', { cache: 'no-store' }).then(function (r) { return r.text(); })
      .then(function (s) { if (s && s !== st) location.reload(); }).catch(function () {});
  }, 5000);
})();
</script>"""


def render_md(runs: list[dict], is_demo: bool) -> str:
    icon = {"PASS": "🟢", "FAIL": "🔴", "OVERRIDE": "🟠", "NOT MEASURED": "⚪"}
    out = ["# 영상 미션 대시보드", "", f"> 생성 {datetime.now():%Y-%m-%d %H:%M} · `python scripts/mission_dashboard.py`로 갱신"]
    if is_demo:
        out += ["> ⚠ 예시 데이터입니다 (실제 실행 아님)"]
    if runs and "status" in runs[0]:
        out += ["", "## 전체", "", "| 영상 | 시작 | 상태 | 완료 | 결과물 |", "|---|---|---|---|---|"]
        for r in runs:
            media = r.get("media") or {}
            res = next((f"`{r['path']}\\{k.replace('/', chr(92))}`" for k in ("final.mp4", "draft.mp4") if k in media), "-")
            out.append(f"| [{r.get('project') or r['intent']}](#{r['intent']}) | {r.get('started', '')} | {r['status']} | {r.get('done', 0)}/5 | {res} |")
    for r in runs:
        head = f"{r.get('project') or r['intent']} — {r.get('title', '')}" if r.get("project") else r["intent"]
        out += ["", "---", "", f'<a id="{r["intent"]}"></a>', "", f"## {head}", "",
                f"> 상태 **{r.get('status', '-')}** · 기록 `aidlc/spaces/{r['space']}/intents/{r['intent']}/`", "",
                "| 미션 | 상태 | 판정 | 통과 | 요약 |", "|---|---|---|---|---|"]
        for c in r["cards"]:
            out.append(f"| {c['code']} {c['label']} | {c['state']} | {icon[c['verdict']]} {c['verdict']} | {c['passed']}/{c['total']} | {c['result'] or '-'} |")
        mk = {True: "✅", False: "❌", None: "⚪"}
        for c in r["cards"]:
            out += ["", f"### {c['code']} {c['label']} 요구사항 — 기능 {c['req_done']}/{c['req_total']} · {c['goal']}", "",
                    "| ID | 해야 할 일 / 통과 기준 | 상태 |", "|---|---|---|"]
            out += [f"| {x['id']} | {x['text']} | {mk[x['done']]} |" for x in c["requirements"]]
            out += [f"| {x['cid']} | {x['text']} ({x['target']}) | {mk[x['pass']]} |" for x in c["criteria"]]
        fails = [f"- {c['code']}: {f}" for c in r["cards"] for f in c["failed"]]
        if fails:
            out += ["", "**미달 항목**", "", *fails]
    if not runs:
        out += ["", "아직 실행이 없습니다. `/aidlc video-mission-video …`로 시작하세요."]
    return "\n".join(out) + "\n"


def serve(port: int) -> int:
    """Live dashboard: / = real runs (falls back to a link to the demo), /demo = sample data,
    /missions = requirement pages index. Loopback only; each load re-reads the AI-DLC records."""
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    class H(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            path = self.path.split("?")[0].split("#")[0]
            ctype = "text/html; charset=utf-8"
            if path.startswith("/media/"):
                return self.media(unquote(path[len("/media/"):]))
            if path in ("/", "/index.html"):
                runs = collect()
                body = render_html(runs, False, "http", stamp()) if runs else render_html([], False, "http", stamp()).replace(
                    "</body>", '<p><a href="/demo">예시 데이터로 보기 →</a></p></body>')
            elif path == "/demo":
                body = render_html(demo(), True, "http")
            elif path == "/data.json":
                body, ctype = json.dumps(collect(), ensure_ascii=False, indent=1), "application/json; charset=utf-8"
            elif path == "/stamp":
                body, ctype = stamp(), "text/plain; charset=utf-8"
            else:
                self.send_error(404)
                return
            data = body.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def media(self, rel: str):
            """Only a known project's final/draft video or contact sheet; byte ranges so the player can seek."""
            parts = rel.split("/", 1)
            allowed = {p.name for p in collect_projects()}
            if len(parts) != 2 or parts[0] not in allowed or parts[1] not in MEDIA:
                self.send_error(404)
                return
            f = (PROJECTS / parts[0] / parts[1]).resolve()
            if PROJECTS.resolve() not in f.parents or not f.is_file():
                self.send_error(404)
                return
            size = f.stat().st_size
            start, end = 0, size - 1
            rng = re.match(r"bytes=(\d*)-(\d*)$", self.headers.get("Range", ""))
            if rng and (rng.group(1) or rng.group(2)):
                if rng.group(1):
                    start = int(rng.group(1))
                    end = min(int(rng.group(2)), size - 1) if rng.group(2) else size - 1
                else:
                    start = max(0, size - int(rng.group(2)))
                if start > end:
                    self.send_error(416)
                    return
                self.send_response(206)
                self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
            else:
                self.send_response(200)
            self.send_header("Content-Type", "video/mp4" if f.suffix == ".mp4" else "image/jpeg")
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Length", str(end - start + 1))
            self.end_headers()
            with f.open("rb") as fh:
                fh.seek(start)
                left = end - start + 1
                try:
                    while left > 0:
                        chunk = fh.read(min(262144, left))
                        if not chunk:
                            break
                        self.wfile.write(chunk)
                        left -= len(chunk)
                except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError):
                    pass  # the player cancelled a range; normal while seeking

        def log_message(self, *args):  # quiet
            pass

    srv = ThreadingHTTPServer(("127.0.0.1", port), H)
    print(f"대시보드: http://127.0.0.1:{port}  (예시: /demo · 데이터: /data.json · 변경 표시: /stamp) — Ctrl+C로 종료", flush=True)
    srv.serve_forever()
    return 0


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--serve", action="store_true", help="live web dashboard on 127.0.0.1 (rebuilt on every load)")
    ap.add_argument("--port", type=int, default=8765)
    a = ap.parse_args()
    if a.serve:
        return serve(a.port)
    runs = demo() if a.demo else collect()
    if a.json:
        print(json.dumps(runs, ensure_ascii=False, indent=1))
        return 0
    OUT.mkdir(exist_ok=True)
    (OUT / "data.json").write_text(json.dumps(runs, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / "index.html").write_text(render_html(runs, a.demo), encoding="utf-8")
    (ROOT / "DASHBOARD.md").write_text(render_md(runs, a.demo), encoding="utf-8")
    print(f"실행 {len(runs)}개 → {OUT / 'index.html'} · {ROOT / 'DASHBOARD.md'}{' (예시)' if a.demo else ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
