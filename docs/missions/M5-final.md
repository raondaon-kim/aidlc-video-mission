# M5 최종 — 요구사항

> M1 기획 → M2 스토리보드 → M3 음악 → M4 시험 렌더 → **M5 최종**

| 항목 | 내용 |
|---|---|
| 목표 | 60fps 완성본과 다음을 위한 배움 1개 |
| 무게 | 무거움 |
| 승인 | 사람 (G5) |
| 입력 | draft 승인된 구성 |
| 결과물 | `projects/<이름>/final.mp4` · `video-lab/index/proposals.md 제안` |
| 스킬 | hyperframes-cli · reel-export (비율 바꿀 때) |
| 시작 조건 | 빈 메모리 2.5GB 이상 · 다른 무거운 작업 없이 혼자 |

## 해야 할 일 (기능)

| ID | 요구사항 | 확인 |
|---|---|---|
| F5.1 | 60fps로 렌더한다 (빈 메모리 4GB 미만이면 워커 1개) | ☐ |
| F5.2 | 비율이 다르면 reel-export로 바꾼다 | ☐ |
| F5.3 | 측정값·렌더 시간·메모리를 proposals.md에 [대기]로 남긴다 | ☐ |

## 통과 기준 (자동 측정)

| ID | 항목 | 기준 |
|---|---|---|
| C5.1 | fps | 60 |
| C5.2 | 길이 | ±0.15초 |
| C5.3 | 초당 컷·몰아치기 | M4와 같음 |
| C5.4 | 소리·음량 | 있음, -14 ±1.5 LUFS |
| C5.5 | 해상도 | 비율대로 1920x1080 · 1080x1920 · 1080x1080 |
| C5.6 | 제안 기록 | proposals.md에 프로젝트 이름 |
| C5.7 | 업로드 형식 | H.264 + yuv420p |

## 판정 방법

1. 감독이 기능 F5.x를 모두 한다.
2. `mission_check.py final`가 기준을 잰다 → `video-mission-final-check.json`.
3. 기준을 하나라도 못 넘으면 승인 문이 안 열린다. 고치고 다시 잰다.
4. 사람만 "Override"로 넘길 수 있고, 그 결정은 기록된다.

요약 파일: `video-mission-final.md` (Mission · Result · Checks · Verdict · Next)
