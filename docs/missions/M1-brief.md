# M1 기획 — 요구사항

> **M1 기획** → M2 스토리보드 → M3 음악 → M4 시험 렌더 → M5 최종

| 항목 | 내용 |
|---|---|
| 목표 | 영상의 목적과 고정 조건을 정한다 |
| 무게 | 가벼움 |
| 승인 | 사람 (G1) |
| 입력 | 사람의 요청 |
| 결과물 | `projects/<이름>/brief.json` · `projects/<이름>/brief.md` |
| 스킬 | SKILLS_INDEX.md 1·6장 |
| 시작 조건 | 없음 |

## 해야 할 일 (기능)

| ID | 요구사항 | 확인 |
|---|---|---|
| F1.1 | 목적·대상·길이·비율·상업 여부·빠르기(fast/explainer)·필수 문구를 한 번에 묻는다 | ☐ |
| F1.2 | 지도 1장에서 줄을 고르고 템플릿 후보를 정한다 | ☐ |
| F1.3 | 프로젝트 폴더와 brief.json / brief.md를 만든다 | ☐ |
| F1.4 | brand-intake로 색·로고·글꼴을 정리한다 (brand.md, MOTION.md) | ☐ |
| F1.5 | 28초를 넘으면 음악 이어 붙이기(long_music)를 켤지 사람에게 확인한다 | ☐ |

## 통과 기준 (자동 측정)

| ID | 항목 | 기준 |
|---|---|---|
| C1.1 | 이름·목적·지도 줄이 있다 | 모두 있음 |
| C1.2 | 길이 | 5~28초 (long_music이면 ~60초) |
| C1.3 | 비율 | 16:9 · 9:16 · 1:1 |
| C1.4 | 상업 여부를 정했다 | true / false |
| C1.5 | 템플릿 또는 스킬 | 1개 이상 |
| C1.6 | 브랜드 색 | hex 2개 이상 |
| C1.7 | 빠르기 | fast / explainer |

## 판정 방법

1. 감독이 기능 F1.x를 모두 한다.
2. `mission_check.py brief`가 기준을 잰다 → `video-mission-brief-check.json`.
3. 기준을 하나라도 못 넘으면 승인 문이 안 열린다. 고치고 다시 잰다.
4. 사람만 "Override"로 넘길 수 있고, 그 결정은 기록된다.

요약 파일: `video-mission-brief.md` (Mission · Result · Checks · Verdict · Next)
