---
slug: video-mission-final
number: 2.95
name: Video Mission 5 - Final Render
plugin: video-mission
phase: inception
execution: CONDITIONAL
condition: Execute under the video scope, once per video, in order.
lead_agent: video-mission-director-agent
support_agents: []
mode: inline
produces:
  - video-mission-final
  - video-mission-final-check
consumes:
  - artifact: video-mission-draft
    required: true
  - artifact: video-mission-draft-check
    required: true
requires_stage:
  - video-mission-draft
sensors:
  - video-mission-check
  - required-sections
scopes:
  - video-mission-video
inputs: video-mission-draft summary and check, video-lab project files
outputs: video-mission-final.md, video-mission-final-check.json (under this stage's record dir, engine-resolved)
---

# Video Mission 5 - Final Render

MANDATORY: Follow stage-protocol.md for approval gates, question format, and completion messages.

**Spec:** `M5` in the director's knowledge `process-spec.md` (functions F5.x, criteria C5.x). Do every F5.x; the check JSON measures every C5.x.

**Mission:** Render the final 60 fps video and leave one learning for next time.

Work happens in `C:\Users\Administrator\.kiro\crew\workspace\video-lab\projects\<name>\` (the name is in `brief.json`); this stage's record dir holds only the summary and the check.

**Heavy mission.** Before the heavy step check free RAM with `powershell -c "[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,1)"`. Below 2.5 GB: stop, say the number, and wait for the person. Run nothing else heavy at the same time.

## Steps

### Step 0: Show the requirements

Read `C:\Users\Administrator\.kiro\crew\workspace\video-lab-tools\docs\missions\M5-final.md` (generated from `docs/missions.json`; the agent copy is `missions.json` in your knowledge). Before any work, show the person that page's two tables - **해야 할 일 (기능)** and **통과 기준** - as they are, in one message, then start. Do not reword the requirement texts.

### Step 1: Do the mission

1. Render `final.mp4` at 60 fps (`-w 1` unless at least 4 GB is free).
2. If the brief aspect is 9:16 and the composition is 16:9, run the `reel-export` skill.
3. Add a `[대기]` entry to `C:\Users\Administrator\.kiro\crew\workspace\video-lab\index\proposals.md` (rule D): what worked, measured numbers, render time, free RAM.

### Step 2: Measure

Run `python C:\Users\Administrator\.kiro\crew\workspace\video-lab\scripts\mission_check.py final --project <name> --out <this stage's record dir>`.
It writes `video-mission-final-check.json`. It measures every criterion (C) on the requirement page from Step 0.
Never edit that file. If a check fails, fix the work and run it again.

### Step 3: Write the mission summary

Write `video-mission-final.md` from its team template (`aidlc/spaces/default/memory/templates/video-mission-final.md`) with exactly these H2 sections, in this order:

- `## Mission` - one line.
- `## Requirements` - one line per requirement of M5 (F ids from the page): `- [x] F5.n text` when done, `- [ ] F5.n text — why not` when not.
- `## Result` - three lines max: what was made, where (absolute path), key numbers.
- `## Checks` - a table copied from the check JSON: C | check | value | target | pass.
- `## Verdict` - `PASS`, `FAIL` or `OVERRIDE` plus one line why.
- `## Next` - up to three lines: what the next mission does or what to fix.

### Step 4: Gate

Open the approval gate. Lead with the verdict, then the requirement checklist (F, from `## Requirements`) and the criteria table (C, from the check JSON), failed items first. The blocking `video-mission-check` sensor keeps the gate shut until every check passes or the person chooses the audited override.
