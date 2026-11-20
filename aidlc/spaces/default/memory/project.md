# Project-Level Rules

> Project-specific specialisation and corrections. Loaded after `org.md` and
> `team.md` as strict-additive guidance.
> Populated by practices-discovery and the self-learning loop.
>
> Use sparingly: most teams don't need a project layer. Reach for it
> only when this specific project needs stable, durable guidance beyond the
> team practice (for example, package-specific release checks or an additional
> regression suite for a legacy component).

## Way of Working

<!-- Project-specific specialisation. Example: -->
<!-- This monorepo requires package-scoped branch names and a package owner -->
<!-- review in addition to the team's normal merge policy. -->
<!-- A project that merges into another branch than team.md names says so on its own line, read before team.md's: -->
<!-- - **Integration branch**: develop -->

## Walking Skeleton

<!-- Project-specific specialisation. Example: -->
<!-- The walking skeleton must exercise the legacy service adapter as well -->
<!-- as the new service boundary. -->

## Testing Posture

<!-- Project-specific specialisation. -->

## Guard Policy

<!-- Project-specific. Mode: strict, relaxed, or off. Strict here holds for every intent, whatever one person asks in chat; relaxed or off here applies to every intent whose policy came from its scope, unless the person sets another; changing this line changes it. A section under the retired Change Control heading, written by an earlier release, is still read. -->

## Deployment

<!-- Project-specific specialisation. -->

## Code Style

<!-- Project-specific specialisation. -->

## Tech Stack

<!-- Technology choices locked for this project. -->

## Decided

<!-- Decisions made in earlier stages that should not be re-asked. -->
<!-- Format: DECIDED: [decision] (Stage [slug], [date]) -->

## Scope Overrides

<!-- Custom scope rules for this project. -->

## Forbidden

<!-- Populated by practices-discovery affirmation gate. -->
<!-- Format: - NEVER [behavior] (affirmed [date]) -->
<!-- Example: - NEVER throw exceptions across service layer boundaries (affirmed 2026-05-17) -->

## Mandated

<!-- Populated by practices-discovery affirmation gate. -->
<!-- Format: - ALWAYS [behavior] (affirmed [date]) -->
<!-- Example: - ALWAYS use Result<T,E> for fallible operations in service layer (affirmed 2026-05-17) -->

## Corrections

<!-- Project-specific corrections from human feedback. -->
<!-- Format: NEVER/ALWAYS [behavior] (learned [date]) -->

## Rules from the video-mission plugin
<!-- plugin:video-mission:rules:0:f69e893b -->
<!-- The video-mission plugin owns this section and plugin sync rewrites it; put the team's own rules in team.md, outside this section. -->
### Video missions (video-mission plugin)

- The video itself lives in `C:\Users\Administrator\.kiro\crew\workspace\video-lab\projects\<name>\`; AI-DLC records live here. Never copy media into the record dir.
- Every video-mission stage ends with `python C:\Users\Administrator\.kiro\crew\workspace\video-lab\scripts\mission_check.py <stage> --project <name> --out <record stage dir>`; its JSON is the only source of the pass/fail verdict.
- Fast-video targets come from `video-lab/index/curated.md` chapter 2 (scene 1.5-2.5 s, burst at 55-75 % with 5-9 cuts 0.2-0.4 s apart, 0.6-0.8 cuts/s).
- Heavy steps (MusicGen, render, HyperFrames check/snapshot) run alone and only with at least 2.5 GB free RAM; below 2 GB stop and tell the person.
- A commercial video must not use MusicGen (CC BY-NC weights).
<!-- /plugin:video-mission:rules:0:f69e893b -->
