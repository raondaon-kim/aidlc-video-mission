# M4 시험 렌더 — 미션 요약

## Mission

스토리보드(12장면, 128 BPM)와 bgm.wav로 15초 Kiro Crew 구성을 만들고 30fps 초안으로 리듬을 실제로 잰다. 지도 줄: 빠른 제품 출시 영상.

## Requirements

- [x] F4.1 템플릿 복사 또는 새 프로젝트 (CLI 버전을 섞지 않는다) — 템플릿 11 복사, hyperframes@0.8.96 하나만 사용. 원본 index.html은 `template11-original.html`로 빼서 루트 구성 1개 유지
- [x] F4.2 스토리보드 시간·전환·음악을 넣는다 — 컷 시각을 storyboard.json 그대로(마디 1.875초, 몰아치기 8분음표 0.234초), bgm.wav를 오디오 트랙으로
- [x] F4.3 30fps, 워커 1개로 렌더한다 — `render -f 30 -w 1`, 1분 20초, 빈 메모리 2.89GB에서 혼자 실행

## Result

15초 16:9 초안 (유령 → 여러 에이전트를. → 한 화면에서. → 대시보드 카드 4개 → 기능 5개 몰아치기+번쩍 → Kiro Crew. → 엔드 카드).
`C:\Users\Administrator\.kiro\crew\workspace\video-lab\projects\kirocrew-promo\draft.mp4` (3.8 MB, 장면 모음 `snapshots/contact-sheet.jpg`)
잰 컷 11개 · 초당 0.73 · 계획 일치 100% · 박자 일치 100% · 3번째 렌더(앞 두 번은 기준 통과, 글자 가독성만 고침).

## Checks

| C | 항목 | 값 | 기준 | 통과 |
|---|---|---|---|---|
| C4.1 | fps | 30.0 | 30 | ✅ |
| C4.2 | 길이(초) | 15.0 | 15.0 ±0.15 | ✅ |
| C4.3 | 초당 컷 | 0.73 | 0.6~0.8 | ✅ |
| C4.4 | 잰 몰아치기 위치 (마지막) | 0.565 | 0.55~0.75 | ✅ |
| C4.5 | 소리 | True | 있음 | ✅ |
| C4.6 | 계획대로 잘림 | 1.0 | ≥0.8 (±0.1s) | ✅ |
| C4.7 | 박자에 컷 | 1.0 | ≥0.8 (±0.05s) | ✅ |

## Verdict

PASS — 7개 기준 모두 통과. 모든 컷을 배경색이 바뀌는 하드 컷으로 만들어 계획 컷이 전부 잡혔다.

## Next

M5 최종 렌더(무거움): 같은 구성을 60fps로 렌더(빈 메모리 4GB 미만이면 워커 1개) → h264/yuv420p 확인 → proposals.md에 kirocrew-promo 기록 → mission_check final.
