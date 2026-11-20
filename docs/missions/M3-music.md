# M3 음악 — 요구사항

> M1 기획 → M2 스토리보드 → **M3 음악** → M4 시험 렌더 → M5 최종

| 항목 | 내용 |
|---|---|
| 목표 | BPM 고정 배경음과 박자 그리드를 만들고 컷을 박자에 맞춘다 |
| 무게 | 무거움 |
| 승인 | 사람 (G3, 들어보고) |
| 입력 | brief.json · storyboard.json |
| 결과물 | `assets/bgm/bgm.wav` · `assets/bgm/bgm.grid.json` · `assets/bgm/report.json` · `박자에 맞춘 storyboard.json` |
| 스킬 | musicgen-trendy (비상업) · 상업이면 구매곡/ACE-Step + post |
| 시작 조건 | 빈 메모리 2.5GB 이상 · 다른 무거운 작업 없이 혼자 |

## 해야 할 일 (기능)

| ID | 요구사항 | 확인 |
|---|---|---|
| F3.1 | 상업 여부로 음원 경로를 고른다 (상업이면 MusicGen 금지) | ☐ |
| F3.2 | 프리셋·BPM·길이로 만들고 BPM 고정·음량 맞춤을 한다 | ☐ |
| F3.3 | 스토리보드 컷을 마디(보통)와 8분음표(몰아치기)에 맞춘다 | ☐ |
| F3.4 | 28초를 넘으면 앞 조각의 끝 4초를 이어받아 다음 조각을 만들고 붙인다 (long_music) | ☐ |

## 통과 기준 (자동 측정)

| ID | 항목 | 기준 |
|---|---|---|
| C3.1 | 길이 | 영상 길이 ±0.05초 |
| C3.2 | BPM | 목표 ±2, 늘림 0.8~1.25배 |
| C3.3 | 음량 | -14 ±1 LUFS |
| C3.4 | 박자 그리드 | bgm.grid.json 있음 |
| C3.5 | 라이선스 | 상업이면 비상업(NC) 불가 |
| C3.6 | 이음새 | 조각 수 맞음, 이음새 앞뒤 음량 차 3dB 이하 (긴 음악만) |

## 판정 방법

1. 감독이 기능 F3.x를 모두 한다.
2. `mission_check.py music`가 기준을 잰다 → `video-mission-music-check.json`.
3. 기준을 하나라도 못 넘으면 승인 문이 안 열린다. 고치고 다시 잰다.
4. 사람만 "Override"로 넘길 수 있고, 그 결정은 기록된다.

요약 파일: `video-mission-music.md` (Mission · Result · Checks · Verdict · Next)
