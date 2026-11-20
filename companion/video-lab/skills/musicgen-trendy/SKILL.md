---
name: musicgen-trendy
description: Make a trendy instrumental background track (no vocals) for a fast motion-graphics video with MusicGen on this PC, locked to an exact BPM, cut to the video length, mastered, with a beat grid JSON (bars, beats, 8th notes, burst window) so scene cuts land on the music. Genre presets - minimal techno, hype sports, trailer hybrid, drift phonk, UK garage, afro house, future bass, synthwave, lofi explainer. Use when someone asks for BGM, background music, a beat, "music for this video", "trendy music", or wants cuts synced to music. NON-COMMERCIAL weights (CC BY-NC) - for commercial videos use ACE-Step instead.
---

# MusicGen trend BGM (video-lab)

Makes **one instrumental bed per video**: MusicGen writes a raw take from a genre prompt, then a light post step locks the tempo to an exact BPM, starts the file on a downbeat, cuts it to the video length, masters it, and writes a **beat grid** the composition uses for cut times.

## 0. License gate (read first)

- `facebook/musicgen-*` weights are **CC BY-NC 4.0 — non-commercial only.** (`repos/audiocraft/LICENSE_weights`)
- OK: internal drafts, pitches, tests, personal/education use without revenue.
- NOT OK: paid ads, client work, monetized channels, company marketing. → Tell the user and switch to **ACE-Step 1.5 (MIT)** or a licensed API (see `research/MUSIC_RESEARCH.md`).
- If you cannot tell whether the video is commercial, **ask once** before generating. Write the answer into `report.json` → `"use"`.

## 1. Where things are

| Thing | Path |
|---|---|
| Python env (torch CPU + transformers) | `tools/musicgen/.venv/Scripts/python.exe` |
| Model weights (offline) | `tools/musicgen/models/musicgen-small` |
| Script | `.claude/skills/musicgen-trendy/scripts/musicgen_bgm.py` |
| Genre presets | `.claude/skills/musicgen-trendy/presets.json` |
| Reference repo (docs only, do not build) | `repos/audiocraft` |

Always run with the venv python:

```bash
PY=tools/musicgen/.venv/Scripts/python.exe
S=.claude/skills/musicgen-trendy/scripts/musicgen_bgm.py
$PY $S presets
```

## 2. Memory rule (this PC: 7.7 GB RAM, no GPU)

| Step | Weight | Rule |
|---|---|---|
| `generate` / `all` (loads MusicGen) | **heavy** | Run **alone**: no render, `check`, `snapshot` or subagent at the same time. Script waits for ≥ 2.5 GB free and stops if it never comes. |
| `post` | light | numpy + ffmpeg, fine anytime |

- Use `musicgen-small` (default). `musicgen-medium` needs far more RAM — not on this PC.
- Weights are loaded as **bfloat16** (`--dtype bf16`, default, ≈ 1.2 GB resident instead of 2.4 GB fp32). Use `--dtype fp32` only when ≥ 4 GB is free.
- `--threads 4` (default). Lower it if the PC lags.
- Expect roughly 1–3 min of CPU per 15 s take. Do not start several takes "to be safe"; 2 takes is the max.

## 3. Pick the preset from the video

Read `SKILLS_INDEX.md` 2장 first: normal scene ≈ 1 bar, burst at 55–75 % with cuts on 8th notes.

| Video | Preset | BPM | Why |
|---|---|---|---|
| Fast tech/product launch, kinetic type | `minimal-techno` | 128 | Steady kick, 8th = 0.234 s fits burst |
| Hype ad, feature cascade | `hype-sports` | 125 | Big hits for each feature |
| Launch opener, logo reveal | `trailer-hybrid` | 120 | Build + hits, 1 bar = 2.0 s |
| Edgy social montage | `drift-phonk` | 140 | Very fast, 8th = 0.214 s |
| Lifestyle / app promo | `uk-garage` | 132 | Trendy shuffle groove |
| Warm brand film | `afro-house` | 122 | Organic, upbeat |
| Colorful SaaS UI demo | `future-bass` | 120 | Bright, playful |
| Retro neon | `synthwave` | 110 | 1 bar = 2.18 s, calmer |
| Lecture / explainer under voice | `lofi-explainer` | 88 | Calm bed, **not** for fast cuts |

Default when the user only says "fast / trendy": **`minimal-techno` at 128**.

## 4. Writing a custom prompt (when no preset fits)

MusicGen listens to **genre + instruments + texture + energy**. Template:

```
{genre}, {drums}, {bass}, {lead or chords}, {texture/space}, {energy words}, instrumental, no vocals
```

Do:
- Name 1 genre, 3–5 concrete instruments, 2 energy words. Keep it under ~40 words.
- End with `instrumental, no vocals` (the script also appends the BPM).
- Use `--extra` to nudge a preset: `--extra "darker, more cowbell"`.

Don't:
- Name artists, songs or labels (copyright risk, and MusicGen ignores them anyway).
- Ask for structure like "drop at 9 s" — MusicGen cannot place sections. Structure comes from the **grid + stutter** in post.
- Ask for vocals or lyrics.

## 5. Make the track

Normal path — generate and post in one go:

```bash
$PY $S all --preset minimal-techno --duration 15 --out projects/<name>/assets/bgm
```

Options that matter:

| Option | Use |
|---|---|
| `--duration 15` | Video length in seconds (max 28; up to 60 with `--long`) |
| `--long` | Over 28 s: first 28 s, then 24 s chunks that continue the last 4 s (audio prompt), joined with a 20 ms crossfade. Seams land in `report.json` → `seams_s`; generation takes 2-3x longer |
| `--bpm 128` | Override preset tempo |
| `--takes 2` | Two seeds, the script keeps the one with the clearest beat nearest the BPM |
| `--seed 7` | Change for a different take; same seed = same result |
| `--stutter` | Audio burst: repeats 16th slices on every 8th inside the 55–75 % window so the music "stutters" with the fast cuts |
| `--extra "..."` | Add words to a preset prompt |
| `--cfg 3.0` | Higher = follows text more, can sound harsher (2.5–4) |

Re-master an existing take without regenerating (light):

```bash
$PY $S post --in projects/<name>/assets/bgm/take_1_raw.wav --bpm 128 --duration 15 --stutter --out projects/<name>/assets/bgm
```

## 6. What you get

`projects/<name>/assets/bgm/`:

| File | Content |
|---|---|
| `bgm.wav` | Final: exact length, target BPM, starts on a downbeat, −14 LUFS, 0.35 s fade |
| `bgm.grid.json` | `bpm`, `beats`, `eighths`, `bars`, `scene_cuts_suggested`, `burst {start,end,eighths}` (seconds) |
| `take_N_raw.wav` | Raw MusicGen takes |
| `report.json` | detected BPM, stretch ratio, chosen take, prompt, seed, license, `chunks`, `seams_s` |

Check `report.json`: if `stretch_ratio` is `1.0` because the take was too far from the BPM (outside 0.8–1.25), say so and make another take with a new `--seed`.

## 7. Sync cuts to the music (HyperFrames)

1. Read `bgm.grid.json`.
2. Normal scenes: start each scene on `scene_cuts_suggested[i]` (one bar each; merge two bars for a longer hold).
3. Burst: inside `burst.start`–`burst.end`, cut or swap visuals on **every** value in `burst.eighths`.
4. Big hits (logo, end card) on a bar start.
5. Add the track to the composition per the `hyperframes` / `media-use` skills (audio element at volume 1.0 for a silent film; ≈ 0.12 under a voice — see `media-use/references/mixing.md`).
6. Add SFX from `media-use/audio/assets/sfx/` on transitions: `whoosh-short` on whips, `impact-bass-1` on bar hits, `glitch-*` in the burst, `riser` into the burst.
7. After render, measure with `python scripts/sample_speed.py`-style analysis and compare with 2장 targets.

## 8. Troubleshooting

| Problem | Fix |
|---|---|
| `STOP: 빈 메모리 …` | Close heavy apps / wait; never lower `--min-free-gb` below 2.0 |
| Sounds muddy / random | New `--seed`, or `--cfg 3.5`, or simpler prompt (fewer instruments) |
| Beat drifts against cuts | Take was outside stretch range → new seed or `--takes 2` |
| Too quiet / too loud | Final is −14 LUFS (social standard); adjust volume in the composition, not the file |
| Model not found offline | Weights live in `tools/musicgen/models/musicgen-small`; without them the script downloads from Hugging Face |

## 9. After the video

Per `CLAUDE.md` rule D, add a `[대기]` entry to `index/proposals.md`: preset, BPM, seed, whether `--stutter` helped, generation time and free RAM.
