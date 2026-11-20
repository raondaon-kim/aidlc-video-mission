# companion/video-lab — 영상 작업 폴더 쪽 파일

AI-DLC 플러그인이 부르는 측정 스크립트와 MusicGen 스킬의 **복사본**입니다.
실제로는 영상 작업 폴더 `video-lab/`에 이 구조 그대로 둡니다.

```
video-lab/
├── scripts/
│   ├── mission_check.py      # 미션 측정 → video-mission-<단계>-check.json (+ .md)
│   └── sample_speed.py       # 컷·장면 길이 측정 (ffmpeg 장면 점수, 컷 ≥ 0.30)
├── .claude/skills/musicgen-trendy/   ← skills/musicgen-trendy/
│   ├── SKILL.md · presets.json · requirements.txt
│   └── scripts/musicgen_bgm.py
├── tools/musicgen/.venv · tools/musicgen/models/musicgen-small   # 직접 설치 (README 참고)
└── projects/<영상 이름>/       # brief.json · storyboard.json · assets/bgm · comp/ · draft.mp4 · final.mp4
```

원본은 `video-lab/`에 있고, 이 폴더는 공개용 스냅샷입니다. 고치면 두 곳을 맞춰 주세요.
