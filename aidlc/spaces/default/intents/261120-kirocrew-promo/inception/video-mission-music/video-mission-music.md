# M3 음악 — 미션 요약

## Mission

128 BPM으로 고정된 15초 배경음과 박자 그리드를 만들고 컷을 박자에 맞춘다. 지도 줄: 빠른 제품 출시 영상.

## Requirements

- [x] F3.1 상업 여부로 음원 경로를 고른다 (상업이면 MusicGen 금지) — 비상업이라 MusicGen 가능, 빈 메모리 2.44GB(<2.5GB)라 사람 선택으로 직접 만든 합성 비트
- [x] F3.2 프리셋·BPM·길이로 만들고 BPM 고정·음량 맞춤을 한다 — 128 BPM, 15.0초, -14.37 LUFS, 몰아치기 구간 끊김(stutter)
- [x] F3.3 스토리보드 컷을 마디(보통)와 8분음표(몰아치기)에 맞춘다 — 모든 컷이 이미 1.875초·0.234초 그리드 위 (어긋남 0초), 수정 없음
- [x] F3.4 28초를 넘으면 앞 조각의 끝 4초를 이어받아 다음 조각을 만들고 붙인다 (long_music) — 15초라 해당 없음

## Result

ffmpeg 합성 비트(킥·하이햇·베이스·아르페지오), 정확히 128 BPM → 박자 고정·첫 박 정렬·음량 맞춤·몰아치기 끊김.
`C:\Users\Administrator\.kiro\crew\workspace\video-lab\projects\kirocrew-promo\assets\bgm\bgm.wav` (+ bgm.grid.json, report.json)
BPM 128.0 · 15.0초 · -14.37 LUFS · 라이선스 자체 제작.

## Checks

| C | 항목 | 값 | 기준 | 통과 |
|---|---|---|---|---|
| C3.1 | 길이(초) | 15.0 | 15.0 ±0.05 | ✅ |
| C3.2 | BPM | 128.0 | 128.0 ±2 | ✅ |
| C3.3 | 음량(LUFS) | -14.37 | -14.0 ±1 | ✅ |
| C3.4 | 박자 그리드 | True | 있음 | ✅ |
| C3.5 | 라이선스 | self-made (no third-party audio) | 상업이면 NC 불가 | ✅ |
| C3.6 | 이음새 | 해당 없음 (28초 이하) | 긴 음악만 | ✅ |

## Verdict

PASS — 6개 기준 모두 통과. 음악은 MusicGen이 아닌 단순 합성 비트(사람 선택).

## Next

M4 시험 렌더(무거움): 템플릿 11 복사(hyperframes@0.8.96) → 스토리보드 시간·bgm.wav 적용 → 30fps, 워커 1개.
빈 메모리 2.5GB 이상일 때만, 혼자 실행.
