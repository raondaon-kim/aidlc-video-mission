<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->

## Deviations
- 2026-11-20T04:40:00Z — 빈 메모리 2.44GB로 MusicGen 시작 기준(2.5GB) 미달. 사람이 고른 대로 ffmpeg 합성 비트로 대신했다.
- 2026-11-20T04:40:00Z — 2·4박 클랩을 넣었더니 박자 읽기가 85 BPM으로 틀렸다. 클랩을 빼고 아르페지오로 바꿔 128.13으로 읽힘.
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
