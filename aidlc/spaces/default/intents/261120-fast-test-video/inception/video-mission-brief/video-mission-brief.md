# M1 기획 — 미션 요약

## Mission

15초 빠른 시험 영상의 목적과 고정 조건을 정한다. 지도 줄: 빠른 글자(키네틱 타입) 영상 → `motion-effects`.

## Requirements

- [x] F1.1 목적·대상·길이·비율·상업 여부·빠르기(fast/explainer)·필수 문구를 한 번에 묻는다
- [x] F1.2 지도 1장에서 줄을 고르고 템플릿 후보를 정한다
- [x] F1.3 프로젝트 폴더와 brief.json / brief.md를 만든다
- [x] F1.4 brand-intake로 색·로고·글꼴을 정리한다 (brand.md, MOTION.md)
- [x] F1.5 28초를 넘으면 음악 이어 붙이기(long_music)를 켤지 사람에게 확인한다 — 15초라 해당 없음, long_music=false

## Result

시험용 15초 · 16:9 · 비상업 · fast · UBION(학습자 대상), 문구 "빠르게. / 정확하게. / 박자에 맞게."
`C:\Users\Administrator\.kiro\crew\workspace\video-lab\projects\ubion-fast-test\` — brief.json, brief.md, brand.md, MOTION.md, CLAUDE.md, assets\brand\ubion-logo.png
색 #051753 · #0068f7 · #0025a0 · #ffffff (ubion.co.kr), 템플릿 24 + 02, 음악 minimal-techno 128 BPM.

## Checks

| C | 항목 | 값 | 기준 | 통과 |
|---|---|---|---|---|
| C1.1 | 이름 | ubion-fast-test | 있음 | ✅ |
| C1.1 | 목적 | 파이프라인 시험용 — video-mission v0.4 제작 흐름과 기준 점검 | 있음 | ✅ |
| C1.1 | 지도 줄 | 빠른 글자(키네틱 타입) 영상 | 있음 | ✅ |
| C1.2 | 길이(초) | 15 | 5~28 | ✅ |
| C1.3 | 비율 | 16:9 | 16:9 · 9:16 · 1:1 | ✅ |
| C1.4 | 상업 여부 | false | true/false | ✅ |
| C1.5 | 템플릿/스킬 | 24-one-time-bundle, 02-showreel-kinetic | 1개 이상 | ✅ |
| C1.6 | 브랜드 색 | #051753, #0068f7, #0025a0, #ffffff | hex 2개 이상 | ✅ |
| C1.7 | 빠르기 | fast | fast / explainer | ✅ |

## Verdict

PASS — 9개 기준 모두 통과.

## Next

M2 스토리보드: 15초를 128 BPM 마디(1.875초)로 나누고, 55~75% 지점에 몰아치기 1구간(5~9컷, 0.234초 간격)을 둔다.
템플릿 24의 카드 벽·격자 바닥과 02의 키네틱 글자를 섞는다. 고양이(18) 같은 캐릭터는 쓰지 않는다.
