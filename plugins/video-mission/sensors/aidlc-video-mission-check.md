---
id: video-mission-check
kind: deterministic
command: bun {{HARNESS_DIR}}/tools/aidlc-sensor-video-mission-check.ts
default_severity: blocking
fire_on: gate
description: Reads a video mission's measured check JSON and passes only when every check meets its target (video-mission plugin, blocking at the gate)
category: document-shape
matches: "**/intents/**"
input_schema:
  output_path: string
  stage_slug: string
output_schema:
  pass: boolean
  findings_count: integer
  mission: string
  failed: string[]
  message: string
timeout_seconds: 10
---

# video-mission-check sensor

BLOCKING at the approval gate. Every video-mission stage writes
`video-mission-<stage>-check.json` with `mission_check.py`:

```json
{ "mission": "music", "checks": [
  { "id": "tempo", "label": "BPM", "value": 128.4, "target": "128 ± 2", "pass": true } ] }
```

The sensor recomputes the verdict from the `checks` list (it does not trust a
top-level `pass`): the gate opens only when the list is non-empty and every
check passes. Any other file it is fired on is a clean pass-through. A missing
or unreadable check JSON for the stage is a failure, so a mission cannot be
approved without being measured. The person can still use the gate's
"Override blocking sensors" choice; that override is audited.
