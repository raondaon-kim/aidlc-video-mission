---
name: video-mission-video
plugin: video-mission
depth: Standard
keywords:
  - video
  - 영상
  - motion graphics
  - 모션 그래픽
description: "Make one video in video-lab: brief, storyboard, music, draft render, final render - each mission measured and gated"
skeleton: off
runner: true
review_cap: none
sensors: on
learnings: on
summary_confirmation: off
plan_approval: off
collaborators: off
---

# video scope

Runs the five video-mission stages for one video in `video-lab`
(`C:\Users\Administrator\.kiro\crew\workspace\video-lab`). Core software
stages are not on this plan.

## Why these stages

Each stage is one production mission with a written summary and a measured
check. A blocking gate sensor reads the check, so a mission that misses its
target cannot be approved until it is fixed or the person overrides it.

| Stage | Mission | Check |
|---|---|---|
| video-mission-brief | purpose, length, ratio, map line, commercial use | required fields, ranges |
| video-mission-storyboard | scene table, burst placement | scene length, burst 55-75 %, cut count |
| video-mission-music | BPM-locked bed + beat grid | tempo, length, loudness, license |
| video-mission-draft | 30 fps draft render | cuts/sec, cut count, burst found |
| video-mission-final | 60 fps final | fps, size, length, audio, loudness |

Reviews are off: the person is the reviewer at each gate. Summary confirmation
and plan approval are off because each stage already stops at its own gate.
