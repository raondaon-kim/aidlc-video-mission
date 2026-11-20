# M5 최종 렌더 — 미션 요약

## Mission

승인된 초안 구성을 60fps 최종본으로 렌더하고 업로드 형식과 리듬이 M4와 같은지 잰다. 지도 줄: 빠른 제품 출시 영상.

## Requirements

- [x] F5.1 60fps로 렌더한다 (빈 메모리 4GB 미만이면 워커 1개) — 빈 메모리 2.75GB라 워커 1개, 2분 16초
- [x] F5.2 비율이 다르면 reel-export로 바꾼다 — brief 16:9 = 구성 16:9, 해당 없음
- [x] F5.3 측정값·렌더 시간·메모리를 proposals.md에 [대기]로 남긴다 — "하드 컷은 배경색을 바꿔야 잡힌다 — kirocrew-promo"

## Result

Kiro Crew 사내 세미나 오프닝 영상 최종본, 15초 · 1920x1080 · 60fps · H.264/yuv420p.
`C:\Users\Administrator\.kiro\crew\workspace\video-lab\projects\kirocrew-promo\final.mp4` (4.5 MB)
초당 컷 0.73 · 몰아치기 56 % · -15.12 LUFS · 렌더 2분 16초.

## Checks

| C | 항목 | 값 | 기준 | 통과 |
|---|---|---|---|---|
| C5.1 | fps | 60.0 | 60 | ✅ |
| C5.2 | 길이(초) | 15.0 | 15.0 ±0.15 | ✅ |
| C5.3 | 초당 컷 | 0.73 | 0.6~0.8 | ✅ |
| C5.3 | 잰 몰아치기 위치 (마지막) | 0.563 | 0.55~0.75 | ✅ |
| C5.4 | 소리 | True | 있음 | ✅ |
| C5.4 | 음량(LUFS) | -15.12 | -14.0 ±1.5 | ✅ |
| C5.5 | 해상도 | 1920x1080 | 1920x1080 | ✅ |
| C5.6 | 제안 기록 | True | proposals.md에 프로젝트 이름 | ✅ |
| C5.7 | 업로드 형식 | h264,yuv420p | h264,yuv420p | ✅ |

## Verdict

PASS — 9개 측정 모두 통과. 리듬이 M4 초안과 같다(0.73, 56 %).

## Next

영상 완성. 사내 발표 전 확인: 유령 아이콘을 공식 Kiro 로고로 바꿀지, MusicGen 음악으로 바꿀지(PC 재시작 후).
proposals.md의 [대기] 제안을 승인하면 curated.md 2장에 반영.
