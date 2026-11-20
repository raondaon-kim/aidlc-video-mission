# M2 스토리보드 — 요구사항

> M1 기획 → **M2 스토리보드** → M3 음악 → M4 시험 렌더 → M5 최종

| 항목 | 내용 |
|---|---|
| 목표 | 모든 장면을 시간 위에 놓고 빠른 리듬을 설계한다 |
| 무게 | 가벼움 |
| 승인 | 사람 (G2) |
| 입력 | brief.json · video-lab/index/curated.md 2장 |
| 결과물 | `projects/<이름>/storyboard.json` · `projects/<이름>/storyboard.md` |
| 스킬 | hyperframes-registry (전환 부품) · SKILLS_INDEX.md 7장 |
| 시작 조건 | 없음 |

## 해야 할 일 (기능)

| ID | 요구사항 | 확인 |
|---|---|---|
| F2.1 | 보통 장면을 1마디(약 2초) 단위로 놓는다 | ☐ |
| F2.2 | fast면 15초마다 몰아치기 1구간(55~75% 위치 기준, 30초면 2구간)을 5~9컷으로 넣는다 | ☐ |
| F2.3 | 장면마다 전환 부품과 글자(5단어 이하)를 정한다 | ☐ |
| F2.4 | 음악 BPM을 정한다 (기본 128) | ☐ |

## 통과 기준 (자동 측정)

| ID | 항목 | 기준 |
|---|---|---|
| C2.1 | 타임라인 빈틈 | 0~길이 전체, 빈틈 0.1초 이하 |
| C2.2 | 보통 장면 평균 | 1.5~2.5초 (explainer 2~5초) |
| C2.3 | 마지막 몰아치기 시작 위치 | 55~75% (fast) |
| C2.4 | 몰아치기마다 컷 수 | 연속 5~9컷 (fast) |
| C2.5 | 몰아치기 컷 간격 | 각 0.2~0.4초 (fast) |
| C2.6 | 장면당 글자 | 5단어 이하 |
| C2.7 | 몰아치기 개수 | 15초당 1개, 최소 1 (fast) |

## 판정 방법

1. 감독이 기능 F2.x를 모두 한다.
2. `mission_check.py storyboard`가 기준을 잰다 → `video-mission-storyboard-check.json`.
3. 기준을 하나라도 못 넘으면 승인 문이 안 열린다. 고치고 다시 잰다.
4. 사람만 "Override"로 넘길 수 있고, 그 결정은 기록된다.

요약 파일: `video-mission-storyboard.md` (Mission · Result · Checks · Verdict · Next)
