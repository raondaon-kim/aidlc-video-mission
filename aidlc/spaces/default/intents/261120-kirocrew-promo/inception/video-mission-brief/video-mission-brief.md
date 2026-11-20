# M1 기획 — 미션 요약

## Mission

사내 교육·세미나 오프닝용 15초 Kiro Crew 소개 영상의 목적과 고정 조건을 정한다. 지도 줄: 빠른 제품 출시 영상.

## Requirements

- [x] F1.1 목적·대상·길이·비율·상업 여부·빠르기(fast/explainer)·필수 문구를 한 번에 묻는다 — 질문 8개(상업 여부는 요청에서 받음): 세미나 오프닝, 15초, 16:9, 비상업, fast, 기능 5개, 3줄+기능 몰아치기, 보라·검정+👻, 모션 그래픽만
- [x] F1.2 지도 1장에서 줄을 고르고 템플릿 후보를 정한다 — "빠른 제품 출시 영상" → 템플릿 11·24·02
- [x] F1.3 프로젝트 폴더와 brief.json / brief.md를 만든다 — `video-lab/projects/kirocrew-promo/`
- [x] F1.4 brand-intake로 색·로고·글꼴을 정리한다 (brand.md, MOTION.md) — kiro.dev에서 색 4개 추출, 유령 아이콘 SVG 직접 그림, 맑은 고딕 Bold
- [x] F1.5 28초를 넘으면 음악 이어 붙이기(long_music)를 켤지 사람에게 확인한다 — 15초라 해당 없음 (long_music false)

## Result

Kiro Crew 홍보영상 기획: 15초 · 16:9 · fast · 비상업, 문구 "여러 에이전트를." → "한 화면에서." → 기능 몰아치기 → "Kiro Crew."
`C:\Users\Administrator\.kiro\crew\workspace\video-lab\projects\kirocrew-promo\` (brief.json, brief.md, brand.md, MOTION.md, CLAUDE.md, assets/brand/kiro-ghost.svg)
색 `#211d25` `#9f63ff` `#c19aff` `#f2f1f4` · 템플릿 11·24·02 · 128 BPM.

## Checks

| C | 항목 | 값 | 기준 | 통과 |
|---|---|---|---|---|
| C1.1 | 이름 | kirocrew-promo | 있음 | ✅ |
| C1.1 | 목적 | 사내 교육·세미나 오프닝 — Kiro Crew가 무엇인지 15초에 빠르게 보여준다 (내부용, 비상업) | 있음 | ✅ |
| C1.1 | 지도 줄 | 빠른 제품 출시 영상 | 있음 | ✅ |
| C1.2 | 길이(초) | 15 | 5~28 (28 초과는 long_music) | ✅ |
| C1.3 | 비율 | 16:9 | 16:9 · 9:16 · 1:1 | ✅ |
| C1.4 | 상업 여부 | False | true/false | ✅ |
| C1.5 | 템플릿/스킬 | 11-synthwave-app-promo, 24-one-time-bundle, 02-showreel-kinetic | 1개 이상 | ✅ |
| C1.6 | 브랜드 색 | #211d25, #9f63ff, #c19aff, #f2f1f4 | hex 2개 이상 | ✅ |
| C1.7 | 빠르기 | fast | fast / explainer | ✅ |

## Verdict

PASS — 9개 측정 모두 통과. 느낌(technical·bold·friendly)과 금지 항목은 답에서 추정했으니 게이트에서 확인 필요.

## Next

M2 스토리보드: 128 BPM 마디에 맞춰 장면 나누기, 기능 5개를 8.44초부터 8분음표 몰아치기로, 끝 카드 1.5초 이상.
