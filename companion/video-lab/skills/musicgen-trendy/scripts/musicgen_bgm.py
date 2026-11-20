"""MusicGen trend BGM for video-lab: generate -> lock tempo -> beat grid -> (stutter) -> master.

Run with the MusicGen venv:
  tools/musicgen/.venv/Scripts/python.exe .claude/skills/musicgen-trendy/scripts/musicgen_bgm.py <command> ...

Commands
  all       generate + post in one go (the normal path)
  generate  text -> raw WAV with MusicGen (heavy: loads the model)
  post      raw WAV -> tempo-locked, mastered WAV + beat grid JSON (light: numpy + ffmpeg)
  presets   list genre presets

Examples
  ... all --preset minimal-techno --duration 15 --out projects/demo/assets/bgm
  ... all --prompt "uk garage, ..." --bpm 132 --duration 20 --takes 2 --stutter
  ... post --in raw.wav --bpm 128 --duration 15 --out projects/demo/assets/bgm

Outputs in --out:
  bgm.wav           final track (exact length, target BPM, -14 LUFS, short fade)
  bgm.grid.json     beats / 8th notes / bars / burst window (55-75 %) in seconds
  take_<n>_raw.wav  raw MusicGen takes (kept for comparison)
  report.json       detected tempo, stretch ratio, chosen take, settings

License: facebook/musicgen-* weights are CC BY-NC 4.0 (NON-COMMERCIAL).
"""
from __future__ import annotations

import argparse
import ctypes
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
LAB = SKILL.parent.parent.parent  # video-lab/.claude/skills/<skill>/scripts -> video-lab
MODELS = LAB / "tools" / "musicgen" / "models"
PRESETS = json.loads((SKILL / "presets.json").read_text(encoding="utf-8"))
SR_POST = 44100
FRAME_RATE = 50          # MusicGen EnCodec tokens per second
MAX_SECONDS = 30         # MusicGen positional limit per pass
MAX_SHORT = 28           # one pass (+2 s headroom); longer needs --long
MAX_LONG = 60            # stitched maximum
FIRST_CHUNK = 28.0       # seconds generated in the first pass
PROMPT_S = 4.0           # tail of the previous chunk fed back as the audio prompt
NEXT_CHUNK = 24.0        # new seconds per continuation (prompt + new stays under the 30 s limit)
BURST = (0.55, 0.75)     # measured burst window (curated.md 2장)


# ---------- memory guard (CLAUDE.md memory rule) ----------

def free_gb() -> float:
    class MS(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    try:
        m = MS(); m.dwLength = ctypes.sizeof(MS)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
        return m.ullAvailPhys / 2**30
    except (AttributeError, OSError):
        return 99.0


def require_memory(need_gb: float) -> None:
    for _ in range(12):
        if free_gb() >= need_gb:
            return
        time.sleep(5)
    sys.exit(f"STOP: 빈 메모리 {free_gb():.1f}GB < {need_gb}GB. 다른 무거운 작업을 끝낸 뒤 다시 실행하세요.")


# ---------- generate (heavy) ----------

def build_prompt(args) -> tuple[str, int]:
    if args.preset:
        p = PRESETS[args.preset]
        prompt, bpm = p["prompt"], args.bpm or p["bpm"]
    else:
        prompt, bpm = args.prompt, args.bpm or 120
    if args.extra:
        prompt = f"{prompt}, {args.extra}"
    # MusicGen follows a stated tempo loosely; saying it still pulls the take closer.
    return f"{prompt}, {bpm} bpm", bpm


def generate(args) -> list[Path]:
    require_memory(args.min_free_gb)
    import torch
    from transformers import AutoProcessor, MusicgenForConditionalGeneration
    import soundfile as sf

    torch.set_num_threads(max(1, min(args.threads, os.cpu_count() or 1)))
    model_dir = MODELS / args.model
    src = str(model_dir) if model_dir.is_dir() else f"facebook/{args.model}"
    processor = AutoProcessor.from_pretrained(src)
    # fp32 weights are 2.3 GB; bfloat16 halves the resident size, which this 7.7 GB PC needs.
    dtype = torch.bfloat16 if args.dtype == "bf16" else torch.float32
    model = MusicgenForConditionalGeneration.from_pretrained(src, torch_dtype=dtype, low_cpu_mem_usage=True)
    model.eval()
    sr = model.config.audio_encoder.sampling_rate

    prompt, bpm = build_prompt(args)
    total = args.duration + 2  # +2 s headroom for trimming to the grid
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    takes = []

    def gen(seconds: float, prompt_audio: np.ndarray | None) -> np.ndarray:
        kw = {"text": [prompt], "padding": True, "return_tensors": "pt"}
        if prompt_audio is not None:  # audio-prompted continuation: the model carries the music on
            kw.update(audio=[prompt_audio], sampling_rate=sr)
        inputs = processor(**kw)
        with torch.inference_mode():
            a = model.generate(**inputs, do_sample=True, guidance_scale=args.cfg,
                               temperature=args.temperature, max_new_tokens=int(seconds * FRAME_RATE))
        return a[0, 0].float().cpu().numpy()

    for i in range(args.takes):
        require_memory(args.min_free_gb - 0.6)  # model already resident
        torch.manual_seed(args.seed + i)
        t0 = time.time()
        first = min(total, FIRST_CHUNK)
        y = gen(first, None)
        seams: list[float] = []
        while len(y) / sr < total - 0.05:
            require_memory(args.min_free_gb - 0.6)
            tail = y[-int(PROMPT_S * sr):]
            new_s = min(NEXT_CHUNK, total - len(y) / sr + 0.5)
            c = gen(new_s, tail)
            # The output starts with the prompt when the model echoes it; drop that part.
            if len(c) > (new_s + 0.5 * PROMPT_S) * sr:
                c = c[len(tail):]
            x = int(0.02 * sr)  # 20 ms crossfade at the seam
            seams.append(round(len(y) / sr, 3))
            y = np.concatenate([y[:-x], y[-x:] * np.linspace(1, 0, x) + c[:x] * np.linspace(0, 1, x), c[x:]])
            print(f"  이어 붙임 {len(seams)}: {len(y) / sr:.1f}s / {total:.1f}s")
        path = out / f"take_{i + 1}_raw.wav"
        sf.write(path, y, sr)
        path.with_suffix(".seams.json").write_text(json.dumps({"chunks": len(seams) + 1, "seams_raw": seams}), encoding="utf-8")
        print(f"take {i + 1}: {len(y) / sr:.1f}s · 조각 {len(seams) + 1} · {time.time() - t0:.0f}s 걸림 · RAM {free_gb():.1f}GB → {path}")
        takes.append(path)
    (out / "prompt.txt").write_text(prompt + "\n", encoding="utf-8")
    del model
    return takes


# ---------- post (light) ----------

def ffmpeg(*args: str) -> None:
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args], check=True)


def load_mono(path: Path, sr: int = 22050) -> np.ndarray:
    raw = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(path),
                          "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32)


def onset_envelope(y: np.ndarray, sr: int = 22050, hop: int = 512, n_fft: int = 2048) -> np.ndarray:
    if len(y) < n_fft:
        return np.zeros(1)
    frames = np.lib.stride_tricks.sliding_window_view(y, n_fft)[::hop] * np.hanning(n_fft)
    mag = np.log1p(np.abs(np.fft.rfft(frames, axis=1)))
    flux = np.maximum(0, np.diff(mag, axis=0)).sum(axis=1)
    flux = flux - np.convolve(flux, np.ones(16) / 16, mode="same")  # remove slow trend
    return np.maximum(flux, 0)


def detect_tempo(y: np.ndarray, sr: int = 22050, hop: int = 512, lo: float = 70, hi: float = 180,
                 target: float | None = None) -> tuple[float, float]:
    """Autocorrelation tempo; when a target is given, prefer the octave nearest to it."""
    env = onset_envelope(y, sr, hop)
    env = env - env.mean()
    ac = np.correlate(env, env, mode="full")[len(env) - 1:]
    fps = sr / hop
    lags = np.arange(len(ac))
    valid = (lags >= fps * 60 / hi) & (lags <= fps * 60 / lo)
    if not valid.any():
        return float(target or 120), 0.0
    lag = int(lags[valid][np.argmax(ac[valid])])
    # Sub-frame precision: parabolic peak fit around the integer lag (a 1-frame step is ~1 % at 128 bpm).
    frac = 0.0
    if 0 < lag < len(ac) - 1:
        y0, y1, y2 = ac[lag - 1], ac[lag], ac[lag + 1]
        den = y0 - 2 * y1 + y2
        frac = 0.5 * (y0 - y2) / den if den else 0.0
    # Averaging the lags of the first few multiples sharpens it further.
    cands = []
    for k in (1, 2, 4, 8):
        c = int(round((lag + frac) * k))
        if c + 1 < len(ac):
            w = max(range(c - 2, c + 3), key=lambda i: ac[i] if 0 <= i < len(ac) else -np.inf)
            y0, y1, y2 = ac[w - 1], ac[w], ac[w + 1]
            den = y0 - 2 * y1 + y2
            cands.append((w + (0.5 * (y0 - y2) / den if den else 0.0)) / k)
    lag_f = float(np.median(cands)) if cands else lag + frac
    bpm = 60 * fps / lag_f
    if target:  # octave errors (x2 / x0.5) are common on drums
        bpm = min((bpm * k for k in (0.5, 1, 2)), key=lambda b: abs(b - target))
    conf = float(ac[lag] / (ac[0] + 1e-9))
    return float(bpm), conf


def beat_phase(y: np.ndarray, bpm: float, sr: int = 22050, hop: int = 512) -> float:
    """Offset (s) of the first beat: the shift whose comb collects the most onset energy."""
    env = onset_envelope(y, sr, hop)
    period = 60 / bpm * sr / hop
    best, best_off = -1.0, 0
    for off in range(int(period)):
        idx = np.arange(off, len(env), period).astype(int)
        s = env[idx[idx < len(env)]].sum()
        if s > best:
            best, best_off = s, off
    return best_off * hop / sr


def atempo_chain(ratio: float) -> str:
    parts = []
    while ratio > 2.0:
        parts.append("atempo=2.0"); ratio /= 2.0
    while ratio < 0.5:
        parts.append("atempo=0.5"); ratio /= 0.5
    parts.append(f"atempo={ratio:.5f}")
    return ",".join(parts)


def stutter(y: np.ndarray, sr: int, grid: dict) -> np.ndarray:
    """Audio 'burst': inside the burst window, repeat each 8th-note's first 16th (stutter edit)."""
    out = y.copy()
    eighth = 60 / grid["bpm"] / 2
    sixteenth = int(eighth / 2 * sr)
    fade = int(0.004 * sr)
    win = np.ones(sixteenth); win[:fade] = np.linspace(0, 1, fade); win[-fade:] = np.linspace(1, 0, fade)
    for t in grid["burst"]["eighths"]:
        a = int(t * sr)
        if a + 2 * sixteenth > len(out):
            break
        piece = y[a:a + sixteenth] * win[:, None] if y.ndim == 2 else y[a:a + sixteenth] * win
        out[a + sixteenth:a + 2 * sixteenth] = piece
    return out


def make_grid(bpm: float, duration: float, offset: float) -> dict:
    beat = 60 / bpm
    beats = [round(offset + i * beat, 4) for i in range(int((duration - offset) / beat) + 1)]
    eighths = [round(offset + i * beat / 2, 4) for i in range(int((duration - offset) / (beat / 2)) + 1)]
    bars = beats[::4]
    b0, b1 = duration * BURST[0], duration * BURST[1]
    burst_e = [t for t in eighths if b0 <= t <= b1]
    return {"bpm": round(bpm, 3), "duration": duration, "offset": round(offset, 4),
            "beat_s": round(beat, 4), "eighth_s": round(beat / 2, 4), "bar_s": round(beat * 4, 4),
            "beats": beats, "eighths": eighths, "bars": bars,
            "scene_cuts_suggested": bars,  # normal scenes = 1 bar (≈1.5–2.5 s at 96–160 bpm)
            "burst": {"start": burst_e[0] if burst_e else None, "end": burst_e[-1] if burst_e else None,
                      "eighths": burst_e, "note": "fast-cut window, cut on every 8th"}}


def post(raw: Path, bpm: float, duration: float, out: Path, do_stutter: bool) -> dict:
    import soundfile as sf
    out.mkdir(parents=True, exist_ok=True)
    y = load_mono(raw)
    found, conf = detect_tempo(y, target=bpm)
    ratio = bpm / found
    if not 0.8 <= ratio <= 1.25:  # beyond this the stretch is audible; keep the take as is
        ratio = 1.0
    tmp = out / "_stretched.wav"
    ffmpeg("-i", str(raw), "-af", atempo_chain(ratio), "-ar", str(SR_POST), "-ac", "2", str(tmp))
    y2, sr = sf.read(tmp, dtype="float32", always_2d=True)
    offset = beat_phase(load_mono(tmp), bpm)
    # Start on the first downbeat so bar 1 = 0 s, then cut to the exact length.
    start = int(offset * sr)
    y2 = y2[start:start + int(duration * sr)]
    side = raw.with_suffix(".seams.json")
    sm = json.loads(side.read_text(encoding="utf-8")) if side.is_file() else {"chunks": 1, "seams_raw": []}
    # seam times follow the stretch (time / ratio) and the downbeat trim (- offset)
    seams = [round(t / ratio - offset, 3) for t in sm["seams_raw"] if 0 < t / ratio - offset < duration]
    if len(y2) < int(duration * sr):
        y2 = np.pad(y2, ((0, int(duration * sr) - len(y2)), (0, 0)))
    grid = make_grid(bpm, duration, 0.0)
    if do_stutter:
        y2 = stutter(y2, sr, grid)
    sf.write(tmp, y2, sr)
    final = out / "bgm.wav"
    fade_at = max(0.0, duration - 0.35)
    ffmpeg("-i", str(tmp), "-af", f"loudnorm=I=-14:TP=-1:LRA=9,afade=t=out:st={fade_at:.2f}:d=0.35",
           "-ar", str(SR_POST), str(final))
    tmp.unlink(missing_ok=True)
    (out / "bgm.grid.json").write_text(json.dumps(grid, indent=1), encoding="utf-8")
    return {"raw": raw.name, "detected_bpm": round(found, 2), "confidence": round(conf, 3),
            "stretch_ratio": round(ratio, 4), "target_bpm": bpm, "duration": duration,
            "stutter": do_stutter, "final": str(final), "chunks": sm["chunks"], "seams_s": seams}


def pick_take(takes: list[Path], bpm: float) -> Path:
    """Prefer the take whose own tempo is closest to the target and whose beat is clearest."""
    scored = []
    for t in takes:
        found, conf = detect_tempo(load_mono(t), target=bpm)
        scored.append((abs(found - bpm) / bpm - conf, t))
    return min(scored)[1]


# ---------- cli ----------

def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg가 PATH에 없습니다.")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("presets")
    for name in ("all", "generate"):
        g = sub.add_parser(name)
        src = g.add_mutually_exclusive_group(required=True)
        src.add_argument("--preset", choices=[k for k in PRESETS if not k.startswith("_")])
        src.add_argument("--prompt")
        g.add_argument("--extra", default="", help="words appended to the prompt (mood, instrument)")
        g.add_argument("--bpm", type=float)
        g.add_argument("--duration", type=float, default=15)
        g.add_argument("--takes", type=int, default=1)
        g.add_argument("--seed", type=int, default=7)
        g.add_argument("--model", default="musicgen-small", choices=["musicgen-small", "musicgen-medium"])
        g.add_argument("--cfg", type=float, default=3.0)
        g.add_argument("--temperature", type=float, default=1.0)
        g.add_argument("--threads", type=int, default=4)
        g.add_argument("--dtype", choices=["bf16", "fp32"], default="bf16",
                       help="bf16 ≈ 1.2 GB resident (default); fp32 ≈ 2.4 GB, only with lots of free RAM")
        g.add_argument("--min-free-gb", type=float, default=2.5)
        g.add_argument("--stutter", action="store_true")
        g.add_argument("--long", action="store_true",
                       help=f"allow {MAX_SHORT + 1}-{MAX_LONG} s: continue the music chunk by chunk (4 s audio prompt)")
        g.add_argument("--out", required=True)
    p = sub.add_parser("post")
    p.add_argument("--in", dest="inp", required=True)
    p.add_argument("--bpm", type=float, required=True)
    p.add_argument("--duration", type=float, default=15)
    p.add_argument("--stutter", action="store_true")
    p.add_argument("--out", required=True)
    a = ap.parse_args()

    if a.cmd == "presets":
        for k, v in PRESETS.items():
            if not k.startswith("_"):
                print(f"{k:16} {v['bpm']:>4} bpm  {v['use']}")
        return 0
    if a.cmd == "post":
        rep = post(Path(a.inp), a.bpm, a.duration, Path(a.out), a.stutter)
        (Path(a.out) / "report.json").write_text(json.dumps(rep, indent=1, ensure_ascii=False), encoding="utf-8")
        print(json.dumps(rep, ensure_ascii=False))
        return 0
    if a.duration > MAX_SHORT and not a.long:
        sys.exit(f"{MAX_SHORT}초를 넘는 음악은 --long 을 켜야 합니다 (조각을 이어 붙임, 생성 시간 2~3배).")
    if a.duration > MAX_LONG:
        sys.exit(f"--duration은 최대 {MAX_LONG}초입니다.")
    takes = generate(a)
    if a.cmd == "generate":
        return 0
    _, bpm = build_prompt(a)
    best = pick_take(takes, bpm) if len(takes) > 1 else takes[0]
    rep = post(best, bpm, a.duration, Path(a.out), a.stutter)
    rep.update({"prompt": build_prompt(a)[0], "takes": len(takes), "seed": a.seed, "model": a.model,
                "license": "CC BY-NC 4.0 (non-commercial)"})
    (Path(a.out) / "report.json").write_text(json.dumps(rep, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(rep, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
