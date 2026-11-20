<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->

## Deviations
- 2026-11-20T03:00:00Z — MusicGen이 모델을 올린 뒤 빈 메모리 1.6GB로 안전장치에 걸려 생성 전에 멈췄다. 사람이 고른 대로 ffmpeg 합성 비트(킥·하이햇·베이스·스탭, 정확히 128 BPM)로 대신했다.
- 2026-11-20T03:00:00Z — 박자 읽기가 1% 틀려(129.2) 그리드가 끝에서 0.14초 밀릴 뻔했다. 포물선 보간 + 배수 평균으로 고쳐 128.12 → 최종 128.0.
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
- 2026-11-20T03:00:00Z — 이 PC에서 MusicGen을 쓰려면 재시작 직후처럼 빈 메모리 3GB 이상이 필요해 보인다. 실제 영상 전에 재시작 후 다시 시험할 것.
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
