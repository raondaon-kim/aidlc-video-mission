# 영상 제작 프로세스 기능정의서 (video-mission)

> **요구사항(F)·기준(C)의 최신 원본은 `docs/missions.json` (v0.4)**, 사람용 페이지는 `docs/missions/`.
> 아래 M1~M5 표는 v0.2 설명용이다. 숫자가 다르면 `missions.json`이 맞다.
> v0.4 변경: 길이 기본 5~28초(28초 초과는 음악 이어 붙이기), 빠르기 fast/explainer, 브랜드 색(C1.6),
> 15초당 몰아치기 1개(C2.7), 이음새(C3.6), 계획대로 잘림(C4.6), 박자에 컷(C4.7), 업로드 형식(C5.7).

- 대상: `video-lab`에서 만드는 15~60초 빠른 모션 그래픽 영상 1편
- 운영: AI-DLC `video-mission` 플러그인 (`/aidlc video-mission-video …`)
- 판정 근거: `video-lab/scripts/mission_check.py` 측정값 → 차단형 센서 `video-mission-check`
- 기준 수치 출처: `video-lab/index/curated.md` 2장 (템플릿 30개 측정, 2026-11-20 승인)

---

## 0. 전체 흐름

```
요청 -> M1 기획 -> M2 스토리보드 -> M3 음악 -> M4 시험 렌더 -> M5 최종 -> 완료
          [G1]        [G2]            [G3]       [G4]            [G5]
```

- 각 미션 = AI-DLC 단계 1개. 끝에 **게이트(G)** 에서 사람이 승인.
- 게이트 전에 측정(C)이 모두 통과해야 문이 열림. 미달이면 사람만 "Override"로 넘김 (감사 기록).
- 산출물(영상·음악)은 `video-lab/projects/<이름>/`, 기록(요약·판정)은 AI-DLC 기록 폴더.

### 역할

| 역할 | 누구 | 하는 일 |
|---|---|---|
| 의뢰·승인자 | 사람 | 요구 입력, 게이트 승인/수정 요청/Override |
| 감독 | `video-mission-director-agent` | 미션 수행, 측정 실행, 요약 작성, 게이트 제시 |
| 측정기 | `mission_check.py` | 파일을 읽어 C 항목 값을 잼. 판단 근거의 유일한 원천 |
| 판정기 | 센서 `video-mission-check` (차단) | 측정 JSON의 모든 C가 통과인지 다시 계산 |
| 양식 검사 | 센서 `required-sections` | 요약이 정해진 H2 5개를 갖췄는지 |

### 상태 (대시보드 공통)

| 기호 | 상태 | 뜻 |
|---|---|---|
| `[ ]` | 대기 | 아직 시작 안 함 |
| `[-]` | 진행 | 미션 수행 중 |
| `[?]` | 승인 대기 | 측정 끝, 게이트에서 사람 대기 |
| `[R]` | 수정 중 | 사람이 수정 요청 |
| `[x]` | 완료 | 승인됨 |
| `[S]` | 건너뜀 | 계획에서 제외 |

판정 배지: **PASS** (C 전부 통과) · **FAIL** (하나라도 미달) · **NOT MEASURED** (측정 JSON 없음) · **OVERRIDE** (미달인데 사람이 넘김)

---

## M1. 기획 (brief)

| 항목 | 내용 |
|---|---|
| 목적 | 영상의 목적과 고정 조건을 정한다 |
| 입력 | 사람의 요청 |
| 출력 | `projects/<이름>/brief.json`, `brief.md` · 요약 `video-mission-brief.md` · 측정 `video-mission-brief-check.json` |
| 무게 | 가벼움 |
| 스킬 | `SKILLS_INDEX.md` 1·6장 |

| 기능 | 정의 |
|---|---|
| F1.1 | 목적·대상·길이·비율·상업 여부·브랜드·필수 문구를 한 번에 묻는다 |
| F1.2 | 지도 1장에서 줄을 고르고 템플릿 후보를 정한다 |
| F1.3 | 프로젝트 폴더와 `brief.json`/`brief.md`를 만든다 |

| 판정 | 측정 id | 기준 |
|---|---|---|
| C1.1 | `name`, `purpose`, `map_row` | 모두 있음 |
| C1.2 | `duration` | 5~60초 |
| C1.3 | `aspect` | 16:9 · 9:16 · 1:1 |
| C1.4 | `commercial` | true/false로 정해짐 |
| C1.5 | `tools` | 템플릿/스킬 1개 이상 |

## M2. 스토리보드 (storyboard)

| 항목 | 내용 |
|---|---|
| 목적 | 모든 장면을 시간 위에 놓고 빠른 리듬을 설계한다 |
| 입력 | `brief.json`, `curated.md` 2장 |
| 출력 | `storyboard.json` (`scenes[]`: start_s, end_s, visual, text, transition, part · `bpm`), `storyboard.md` |
| 무게 | 가벼움 |

| 기능 | 정의 |
|---|---|
| F2.1 | 보통 장면을 1마디(약 2초) 단위로 배치한다 |
| F2.2 | 몰아치기 1구간을 55~75% 지점에 5~9컷으로 넣는다 |
| F2.3 | 장면마다 전환 부품(`whip-pan-cut` 등)과 글자(≤5단어)를 정한다 |
| F2.4 | 음악 BPM을 정한다 (기본 128) |

| 판정 | 측정 id | 기준 |
|---|---|---|
| C2.1 | `coverage` | 0~길이 전체, 빈틈 ≤0.1초 |
| C2.2 | `normal_avg` | 보통 장면 평균 1.5~2.5초 |
| C2.3 | `burst_pos` | 몰아치기 시작 55~75% |
| C2.4 | `burst_cuts` | 연속 5~9컷 |
| C2.5 | `burst_gap` | 각 0.2~0.4초 |
| C2.6 | `words` | 장면당 ≤5단어 |

## M3. 음악 (music)

| 항목 | 내용 |
|---|---|
| 목적 | BPM 고정 배경음과 박자 그리드를 만들고 컷을 박자에 맞춘다 |
| 입력 | `brief.json`, `storyboard.json` |
| 출력 | `assets/bgm/bgm.wav`, `bgm.grid.json`, `report.json`, 박자에 맞춘 `storyboard.json` |
| 무게 | **무거움** (빈 메모리 ≥2.5GB, 혼자) |
| 스킬 | `musicgen-trendy` (비상업) · 상업이면 구매곡/ACE-Step + `post` |

| 기능 | 정의 |
|---|---|
| F3.1 | 상업 여부로 음원 경로를 고른다 (상업이면 MusicGen 금지) |
| F3.2 | 프리셋·BPM·길이로 생성하고 BPM 고정·마스터링한다 |
| F3.3 | 스토리보드 컷을 마디(보통)·8분음표(몰아치기)에 맞춘다 |

| 판정 | 측정 id | 기준 |
|---|---|---|
| C3.1 | `length` | 길이 ±0.05초 |
| C3.2 | `tempo` | 목표 BPM ±2, 늘림 비율 0.8~1.25 |
| C3.3 | `loudness` | -14 ±1 LUFS |
| C3.4 | `grid` | `bgm.grid.json` 있음 |
| C3.5 | `license` | 상업이면 NC 라이선스 불가 |

## M4. 시험 렌더 (draft)

| 항목 | 내용 |
|---|---|
| 목적 | 구성을 만들고 30fps 초안으로 리듬을 실측한다 |
| 입력 | `storyboard.json`, `bgm.wav`, 템플릿 |
| 출력 | `projects/<이름>/draft.mp4` |
| 무게 | **무거움** (`-w 1`) |
| 스킬 | `opus-5-5-video-templates`(0.8.96 고정) 또는 `hyperframes*`, `hyperframes-registry` |

| 기능 | 정의 |
|---|---|
| F4.1 | 템플릿 복사 또는 새 프로젝트 (CLI 버전 섞지 않음) |
| F4.2 | 스토리보드 시간·전환·음악을 적용한다 |
| F4.3 | 30fps, 워커 1개로 렌더한다 |

| 판정 | 측정 id | 기준 |
|---|---|---|
| C4.1 | `fps` | 30 |
| C4.2 | `length` | 길이 ±0.15초 |
| C4.3 | `cuts_per_sec` | 0.6~0.8 |
| C4.4 | `burst` | 측정된 몰아치기 55~75% |
| C4.5 | `audio` | 소리 있음 |

## M5. 최종 (final)

| 항목 | 내용 |
|---|---|
| 목적 | 60fps 완성본과 다음을 위한 배움 1개 |
| 출력 | `projects/<이름>/final.mp4`, `video-lab/index/proposals.md` 제안 |
| 무게 | **무거움** |
| 스킬 | `hyperframes-cli`, 필요 시 `reel-export` |

| 기능 | 정의 |
|---|---|
| F5.1 | 60fps로 렌더한다 (빈 메모리 4GB 미만이면 `-w 1`) |
| F5.2 | 비율이 다르면 `reel-export`로 변환한다 |
| F5.3 | 측정값·렌더 시간·메모리를 `proposals.md`에 `[대기]`로 남긴다 |

| 판정 | 측정 id | 기준 |
|---|---|---|
| C5.1 | `fps` | 60 |
| C5.2 | `length` | 길이 ±0.15초 |
| C5.3 | `cuts_per_sec`, `burst` | M4와 같음 |
| C5.4 | `audio`, `loudness` | 소리 있음, -14 ±1.5 LUFS |
| C5.5 | `size` | 1920x1080 · 1080x1920 · 1080x1080 (비율대로) |
| C5.6 | `proposal` | `proposals.md`에 프로젝트 이름 |

---

## 6. 미션 요약 규격 (모든 미션 공통)

파일: `video-mission-<미션>.md` — 아래 H2 6개를 이 순서로 (센서 `required-sections`가 검사).
단계별 요구사항 원본은 `docs/missions.json`, 사람이 보는 페이지는 `docs/missions/M<n>-<미션>.md`
(`python scripts/build_mission_docs.py`로 생성). 단계 시작 때 이 페이지의 두 표를 먼저 보여준다.

| H2 | 내용 | 길이 |
|---|---|---|
| `## Mission` | 미션 한 줄 + 사용한 지도 줄 | 1~2줄 |
| `## Requirements` | 기능(F) 체크리스트: `- [x] F3.1 …` / `- [ ] F3.2 … — 이유` | F 수만큼 |
| `## Result` | 무엇을 만들었고 어디 있는지(절대경로), 핵심 숫자 | ≤3줄 |
| `## Checks` | 측정 JSON 그대로 표: C id · 항목 · 값 · 기준 · 통과 | 표 |
| `## Verdict` | `PASS` / `FAIL` / `OVERRIDE` + 이유 한 줄 | 1~2줄 |
| `## Next` | 다음 미션에서 할 일 또는 고칠 일 | ≤3줄 |

## 7. 대시보드 데이터 규격

| 카드 필드 | 출처 |
|---|---|
| 상태 | `aidlc-state.md`의 `## Stage Progress` 체크 기호 |
| 판정 배지 | `video-mission-<미션>-check.json`의 `checks[].pass` |
| 통과 수 | 통과 C 수 / 전체 C 수 |
| 실패 항목 | `pass=false`인 항목의 label·value·target |
| 요약 | 요약 `.md`의 `## Result` 첫 줄 |
| 측정 시각 | 측정 JSON `measured_at` |

## 8. 바꾸는 법

- 기준 숫자: `video-lab/index/curated.md` 2장 승인 → `mission_check.py` 상수 → 이 문서 C 표.
- 미션·기능: `plugins/video-mission/stages/inception/*.md` → build → sync (README 참고).
- 요약 양식: `aidlc/spaces/default/memory/templates/video-mission-*.md`.
