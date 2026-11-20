## Video missions (video-mission plugin)

- The video itself lives in `C:\Users\Administrator\.kiro\crew\workspace\video-lab\projects\<name>\`; AI-DLC records live here. Never copy media into the record dir.
- Every video-mission stage ends with `python C:\Users\Administrator\.kiro\crew\workspace\video-lab\scripts\mission_check.py <stage> --project <name> --out <record stage dir>`; its JSON is the only source of the pass/fail verdict.
- Fast-video targets come from `video-lab/index/curated.md` chapter 2 (scene 1.5-2.5 s, burst at 55-75 % with 5-9 cuts 0.2-0.4 s apart, 0.6-0.8 cuts/s).
- Heavy steps (MusicGen, render, HyperFrames check/snapshot) run alone and only with at least 2.5 GB free RAM; below 2 GB stop and tell the person.
- A commercial video must not use MusicGen (CC BY-NC weights).
