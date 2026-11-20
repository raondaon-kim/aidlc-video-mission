---
slug: video-mission-storyboard
number: 2.92
name: Video Mission 2 - Storyboard
plugin: video-mission
phase: inception
execution: CONDITIONAL
condition: Execute under the video scope, once per video, in order.
lead_agent: video-mission-director-agent
support_agents: []
mode: inline
produces:
  - video-mission-storyboard
  - video-mission-storyboard-check
consumes:
  - artifact: video-mission-brief
    required: true
  - artifact: video-mission-brief-check
    required: true
requires_stage:
  - video-mission-brief
sensors:
  - video-mission-check
  - required-sections
scopes:
  - video-mission-video
inputs: video-mission-brief summary and check, video-lab project files
outputs: video-mission-storyboard.md, video-mission-storyboard-check.json (under this stage's record dir, engine-resolved)
---

# Video Mission 2 - Storyboard

MANDATORY: Follow stage-protocol.md for approval gates, question format, and completion messages.

**Spec:** `M2` in the director's knowledge `process-spec.md` (functions F2.x, criteria C2.x). Do every F2.x; the check JSON measures every C2.x.

**Mission:** Lay out every scene on the timeline with the fast-video rhythm.

Work happens in `C:\Users\Administrator\.kiro\crew\workspace\video-lab\projects\<name>\` (the name is in `brief.json`); this stage's record dir holds only the summary and the check.

## Steps

### Step 0: Show the requirements

Read `C:\Users\Administrator\.kiro\crew\workspace\video-lab-tools\docs\missions\M2-storyboard.md` (generated from `docs/missions.json`; the agent copy is `missions.json` in your knowledge). Before any work, show the person that page's two tables - **해야 할 일 (기능)** and **통과 기준** - as they are, in one message, then start. Do not reword the requirement texts.

### Step 1: Do the mission

1. Read `brief.json`. Read `C:\Users\Administrator\.kiro\crew\workspace\video-lab\index\curated.md` chapter 2 (fast-video defaults).
2. Write `storyboard.json`: `scenes[]` of `{start_s, end_s, visual, text, transition, part}` where `part` is `normal` or `burst`, plus `bpm` (planned music tempo).
3. `pace: fast`: normal scenes about one bar each; one burst block of 5-9 cuts (0.2-0.4 s) per 15 s of video, the last one starting at 55-75 %. `pace: explainer`: no bursts, scenes 2-5 s.
4. Transitions from the registry list (`whip-pan-cut`, `flash-through-white`, `match-cut` ...). Write `storyboard.md` as a table the person can read.

### Step 2: Measure

Run `python C:\Users\Administrator\.kiro\crew\workspace\video-lab\scripts\mission_check.py storyboard --project <name> --out <this stage's record dir>`.
It writes `video-mission-storyboard-check.json`. It measures every criterion (C) on the requirement page from Step 0.
Never edit that file. If a check fails, fix the work and run it again.

### Step 3: Write the mission summary

Write `video-mission-storyboard.md` from its team template (`aidlc/spaces/default/memory/templates/video-mission-storyboard.md`) with exactly these H2 sections, in this order:

- `## Mission` - one line.
- `## Requirements` - one line per requirement of M2 (F ids from the page): `- [x] F2.n text` when done, `- [ ] F2.n text — why not` when not.
- `## Result` - three lines max: what was made, where (absolute path), key numbers.
- `## Checks` - a table copied from the check JSON: C | check | value | target | pass.
- `## Verdict` - `PASS`, `FAIL` or `OVERRIDE` plus one line why.
- `## Next` - up to three lines: what the next mission does or what to fix.

### Step 4: Gate

Open the approval gate. Lead with the verdict, then the requirement checklist (F, from `## Requirements`) and the criteria table (C, from the check JSON), failed items first. The blocking `video-mission-check` sensor keeps the gate shut until every check passes or the person chooses the audited override.
