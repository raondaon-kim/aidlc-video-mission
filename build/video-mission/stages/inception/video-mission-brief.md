---
slug: video-mission-brief
number: 2.91
name: Video Mission 1 - Brief
plugin: video-mission
phase: inception
execution: CONDITIONAL
condition: Execute under the video scope, once per video, in order.
lead_agent: video-mission-director-agent
support_agents: []
mode: inline
produces:
  - video-mission-brief
  - video-mission-brief-check
consumes: []
requires_stage: []
sensors:
  - video-mission-check
  - required-sections
scopes:
  - video-mission-video
inputs: brief from the person, video-lab project files
outputs: video-mission-brief.md, video-mission-brief-check.json (under this stage's record dir, engine-resolved)
---

# Video Mission 1 - Brief

MANDATORY: Follow stage-protocol.md for approval gates, question format, and completion messages.

**Spec:** `M1` in the director's knowledge `process-spec.md` (functions F1.x, criteria C1.x). Do every F1.x; the check JSON measures every C1.x.

**Mission:** Decide what the video is for and its hard limits.

Work happens in `C:\Users\Administrator\.kiro\crew\workspace\video-lab\projects\<name>\` (the name is in `brief.json`); this stage's record dir holds only the summary and the check.

## Steps

### Step 0: Show the requirements

Read `C:\Users\Administrator\.kiro\crew\workspace\video-lab-tools\docs\missions\M1-brief.md` (generated from `docs/missions.json`; the agent copy is `missions.json` in your knowledge). Before any work, show the person that page's two tables - **해야 할 일 (기능)** and **통과 기준** - as they are, in one message, then start. Do not reword the requirement texts.

### Step 1: Do the mission

1. Ask the person (one structured question set): purpose / audience, length in seconds, aspect ratio (16:9, 9:16, 1:1), commercial use (yes/no), pace (`fast` or `explainer`), product or brand name, must-say lines.
2. If the length is over 28 s, ask whether to turn on stitched music (`long_music`, up to 60 s, generation takes 2-3x longer). If not, cap the length at 28 s.
3. Pick the map row from `C:\Users\Administrator\.kiro\crew\workspace\video-lab\SKILLS_INDEX.md` chapter 1 and the template candidate(s) from chapter 6.
4. Run the `brand-intake` skill in `C:\Users\Administrator\.kiro\crew\workspace\video-lab` for colours, logo and font (brand.md, MOTION.md).
5. Create `C:\Users\Administrator\.kiro\crew\workspace\video-lab\projects\<name>\` and write `brief.json` (`name, purpose, duration_s, aspect, commercial, pace, long_music, colors[], map_row, templates[], brand, lines[]`) and `brief.md`.

### Step 2: Measure

Run `python C:\Users\Administrator\.kiro\crew\workspace\video-lab\scripts\mission_check.py brief --project <name> --out <this stage's record dir>`.
It writes `video-mission-brief-check.json`. It measures every criterion (C) on the requirement page from Step 0.
Never edit that file. If a check fails, fix the work and run it again.

### Step 3: Write the mission summary

Write `video-mission-brief.md` from its team template (`aidlc/spaces/default/memory/templates/video-mission-brief.md`) with exactly these H2 sections, in this order:

- `## Mission` - one line.
- `## Requirements` - one line per requirement of M1 (F ids from the page): `- [x] F1.n text` when done, `- [ ] F1.n text — why not` when not.
- `## Result` - three lines max: what was made, where (absolute path), key numbers.
- `## Checks` - a table copied from the check JSON: C | check | value | target | pass.
- `## Verdict` - `PASS`, `FAIL` or `OVERRIDE` plus one line why.
- `## Next` - up to three lines: what the next mission does or what to fix.

### Step 4: Gate

Open the approval gate. Lead with the verdict, then the requirement checklist (F, from `## Requirements`) and the criteria table (C, from the check JSON), failed items first. The blocking `video-mission-check` sensor keeps the gate shut until every check passes or the person chooses the audited override.
