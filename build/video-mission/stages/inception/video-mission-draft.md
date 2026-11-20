---
slug: video-mission-draft
number: 2.94
name: Video Mission 4 - Draft Render
plugin: video-mission
phase: inception
execution: CONDITIONAL
condition: Execute under the video scope, once per video, in order.
lead_agent: video-mission-director-agent
support_agents: []
mode: inline
produces:
  - video-mission-draft
  - video-mission-draft-check
consumes:
  - artifact: video-mission-music
    required: true
  - artifact: video-mission-music-check
    required: true
requires_stage:
  - video-mission-music
sensors:
  - video-mission-check
  - required-sections
scopes:
  - video-mission-video
inputs: video-mission-music summary and check, video-lab project files
outputs: video-mission-draft.md, video-mission-draft-check.json (under this stage's record dir, engine-resolved)
---

# Video Mission 4 - Draft Render

MANDATORY: Follow stage-protocol.md for approval gates, question format, and completion messages.

**Spec:** `M4` in the director's knowledge `process-spec.md` (functions F4.x, criteria C4.x). Do every F4.x; the check JSON measures every C4.x.

**Mission:** Build the composition and render a 30 fps draft, then measure its rhythm.

Work happens in `C:\Users\Administrator\.kiro\crew\workspace\video-lab\projects\<name>\` (the name is in `brief.json`); this stage's record dir holds only the summary and the check.

**Heavy mission.** Before the heavy step check free RAM with `powershell -c "[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,1)"`. Below 2.5 GB: stop, say the number, and wait for the person. Run nothing else heavy at the same time.

## Steps

### Step 0: Show the requirements

Read `C:\Users\Administrator\.kiro\crew\workspace\video-lab-tools\docs\missions\M4-draft.md` (generated from `docs/missions.json`; the agent copy is `missions.json` in your knowledge). Before any work, show the person that page's two tables - **해야 할 일 (기능)** and **통과 기준** - as they are, in one message, then start. Do not reword the requirement texts.

### Step 1: Do the mission

1. Copy the chosen template with `opus-5-5-video-templates` (pinned `hyperframes@0.8.96`) or scaffold a new project; never mix the two CLI versions in one project.
2. Apply the storyboard: scene timing from `storyboard.json`, transitions from the registry, add `assets/bgm/bgm.wav`.
3. Render `draft.mp4` at 30 fps with one worker (`-w 1`).

### Step 2: Measure

Run `python C:\Users\Administrator\.kiro\crew\workspace\video-lab\scripts\mission_check.py draft --project <name> --out <this stage's record dir>`.
It writes `video-mission-draft-check.json`. It measures every criterion (C) on the requirement page from Step 0.
Never edit that file. If a check fails, fix the work and run it again.

### Step 3: Write the mission summary

Write `video-mission-draft.md` from its team template (`aidlc/spaces/default/memory/templates/video-mission-draft.md`) with exactly these H2 sections, in this order:

- `## Mission` - one line.
- `## Requirements` - one line per requirement of M4 (F ids from the page): `- [x] F4.n text` when done, `- [ ] F4.n text — why not` when not.
- `## Result` - three lines max: what was made, where (absolute path), key numbers.
- `## Checks` - a table copied from the check JSON: C | check | value | target | pass.
- `## Verdict` - `PASS`, `FAIL` or `OVERRIDE` plus one line why.
- `## Next` - up to three lines: what the next mission does or what to fix.

### Step 4: Gate

Open the approval gate. Lead with the verdict, then the requirement checklist (F, from `## Requirements`) and the criteria table (C, from the check JSON), failed items first. The blocking `video-mission-check` sensor keeps the gate shut until every check passes or the person chooses the audited override.
