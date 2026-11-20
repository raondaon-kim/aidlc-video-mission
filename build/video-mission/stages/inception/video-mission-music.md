---
slug: video-mission-music
number: 2.93
name: Video Mission 3 - Music
plugin: video-mission
phase: inception
execution: CONDITIONAL
condition: Execute under the video scope, once per video, in order.
lead_agent: video-mission-director-agent
support_agents: []
mode: inline
produces:
  - video-mission-music
  - video-mission-music-check
consumes:
  - artifact: video-mission-storyboard
    required: true
  - artifact: video-mission-storyboard-check
    required: true
requires_stage:
  - video-mission-storyboard
sensors:
  - video-mission-check
  - required-sections
scopes:
  - video-mission-video
inputs: video-mission-storyboard summary and check, video-lab project files
outputs: video-mission-music.md, video-mission-music-check.json (under this stage's record dir, engine-resolved)
---

# Video Mission 3 - Music

MANDATORY: Follow stage-protocol.md for approval gates, question format, and completion messages.

**Spec:** `M3` in the director's knowledge `process-spec.md` (functions F3.x, criteria C3.x). Do every F3.x; the check JSON measures every C3.x.

**Mission:** Make the BPM-locked music bed and its beat grid.

Work happens in `C:\Users\Administrator\.kiro\crew\workspace\video-lab\projects\<name>\` (the name is in `brief.json`); this stage's record dir holds only the summary and the check.

**Heavy mission.** Before the heavy step check free RAM with `powershell -c "[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,1)"`. Below 2.5 GB: stop, say the number, and wait for the person. Run nothing else heavy at the same time.

## Steps

### Step 0: Show the requirements

Read `C:\Users\Administrator\.kiro\crew\workspace\video-lab-tools\docs\missions\M3-music.md` (generated from `docs/missions.json`; the agent copy is `missions.json` in your knowledge). Before any work, show the person that page's two tables - **해야 할 일 (기능)** and **통과 기준** - as they are, in one message, then start. Do not reword the requirement texts.

### Step 1: Do the mission

1. If `brief.json` says commercial: do NOT use MusicGen - stop and ask the person for a licensed track or ACE-Step; place it at `assets/bgm/bgm.wav` and run the `musicgen-trendy` script's `post` step on it.
2. Otherwise follow `C:\Users\Administrator\.kiro\crew\workspace\video-lab\.claude\skills\musicgen-trendy\SKILL.md`: `all --preset <from map> --bpm <storyboard bpm> --duration <brief duration> --stutter --out C:\Users\Administrator\.kiro\crew\workspace\video-lab\projects\<name>\assets\bgm`, adding `--long` when `long_music` is true (over 28 s: the music is continued chunk by chunk from a 4 s audio prompt).
3. Snap the storyboard cut times to `bgm.grid.json` (bars for normal scenes, eighths in the burst) and save `storyboard.json` again.

### Step 2: Measure

Run `python C:\Users\Administrator\.kiro\crew\workspace\video-lab\scripts\mission_check.py music --project <name> --out <this stage's record dir>`.
It writes `video-mission-music-check.json`. It measures every criterion (C) on the requirement page from Step 0.
Never edit that file. If a check fails, fix the work and run it again.

### Step 3: Write the mission summary

Write `video-mission-music.md` from its team template (`aidlc/spaces/default/memory/templates/video-mission-music.md`) with exactly these H2 sections, in this order:

- `## Mission` - one line.
- `## Requirements` - one line per requirement of M3 (F ids from the page): `- [x] F3.n text` when done, `- [ ] F3.n text — why not` when not.
- `## Result` - three lines max: what was made, where (absolute path), key numbers.
- `## Checks` - a table copied from the check JSON: C | check | value | target | pass.
- `## Verdict` - `PASS`, `FAIL` or `OVERRIDE` plus one line why.
- `## Next` - up to three lines: what the next mission does or what to fix.

### Step 4: Gate

Open the approval gate. Lead with the verdict, then the requirement checklist (F, from `## Requirements`) and the criteria table (C, from the check JSON), failed items first. The blocking `video-mission-check` sensor keeps the gate shut until every check passes or the person chooses the audited override.
