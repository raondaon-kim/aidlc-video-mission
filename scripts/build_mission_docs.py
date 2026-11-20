"""Build the per-stage requirement views from docs/missions.json.

  python scripts/build_mission_docs.py

Writes:
  docs/missions/M<n>-<slug>.md   one page per mission (for people, AIDLC-VIEWER, the gate)
  plugins/video-mission/knowledge/video-mission-director-agent/missions.json  (agent copy)
Then rebuild + sync the plugin if the agent copy changed (see README).
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "docs" / "missions.json"
OUT = ROOT / "docs" / "missions"
AGENT = ROOT / "plugins" / "video-mission" / "knowledge" / "video-mission-director-agent"


def page(m: dict, flow: str) -> str:
    L = [f"# {m['code']} {m['label']} — 요구사항", "", f"> {flow}", "",
         "| 항목 | 내용 |", "|---|---|",
         f"| 목표 | {m['goal']} |", f"| 무게 | {m['weight']} |", f"| 승인 | {m['approver']} |",
         f"| 입력 | {' · '.join(m['inputs'])} |", f"| 결과물 | {' · '.join(f'`{o}`' for o in m['outputs'])} |",
         f"| 스킬 | {' · '.join(m['skills'])} |",
         f"| 시작 조건 | {' · '.join(m.get('preconditions') or ['없음'])} |", "",
         "## 해야 할 일 (기능)", "", "| ID | 요구사항 | 확인 |", "|---|---|---|"]
    L += [f"| {r['id']} | {r['text']} | ☐ |" for r in m["requirements"]]
    L += ["", "## 통과 기준 (자동 측정)", "", "| ID | 항목 | 기준 |", "|---|---|---|"]
    L += [f"| {c['cid']} | {c['text']} | {c['target']} |" for c in m["criteria"]]
    L += ["", "## 판정 방법", "",
          f"1. 감독이 기능 {m['requirements'][0]['id'].split('.')[0]}.x를 모두 한다.",
          f"2. `mission_check.py {m['slug']}`가 기준을 잰다 → `video-mission-{m['slug']}-check.json`.",
          "3. 기준을 하나라도 못 넘으면 승인 문이 안 열린다. 고치고 다시 잰다.",
          "4. 사람만 \"Override\"로 넘길 수 있고, 그 결정은 기록된다.", "",
          f"요약 파일: `video-mission-{m['slug']}.md` (Mission · Result · Checks · Verdict · Next)", ""]
    return "\n".join(L)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    ms = spec["missions"]
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("M*.md"):
        old.unlink()
    for m in ms:
        flow = " → ".join(f"**{x['code']} {x['label']}**" if x is m else f"{x['code']} {x['label']}" for x in ms)
        (OUT / f"{m['code']}-{m['slug']}.md").write_text(page(m, flow), encoding="utf-8", newline="\n")
    rules = [f"- **{k}**: {v}" for k, v in (spec.get("_rules") or {}).items()]
    idx = ["# 미션별 요구사항", "", f"버전 {spec['version']} · 원본 `docs/missions.json`", "", "## 공통 규칙", "", *rules, "",
           "| 미션 | 목표 | 기능 | 기준 | 무게 | 승인 |", "|---|---|---|---|---|---|"]
    idx += [f"| [{m['code']} {m['label']}]({m['code']}-{m['slug']}.md) | {m['goal']} | {len(m['requirements'])} | {len(m['criteria'])} | {m['weight']} | {m['approver']} |" for m in ms]
    (OUT / "README.md").write_text("\n".join(idx) + "\n", encoding="utf-8", newline="\n")
    AGENT.mkdir(parents=True, exist_ok=True)
    before = (AGENT / "missions.json").read_bytes() if (AGENT / "missions.json").is_file() else b""
    shutil.copyfile(SPEC, AGENT / "missions.json")
    changed = before != SPEC.read_bytes()
    print(f"페이지 {len(ms)}개 + 목록 → {OUT}")
    print("에이전트 사본 바뀜: 플러그인 build + sync 필요" if changed else "에이전트 사본 그대로")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
