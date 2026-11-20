// aidlc-sensor-video-mission-check.ts — BLOCKING gate sensor (video-mission plugin).
//
// Fired once per deliverable at the approval gate. Acts only on
// video-mission-<stage>-check.json (written by video-lab/scripts/mission_check.py);
// every other file is a clean pass-through. The verdict is recomputed from the
// `checks` array, never taken from a top-level `pass`, so a hand-edited summary
// field cannot open the gate. Self-contained: no import of framework libs.
import { existsSync, readFileSync, readdirSync } from "node:fs";
import { basename, dirname, join } from "node:path";

interface Check { id?: string; label?: string; value?: unknown; target?: unknown; pass?: unknown }
interface Result { pass: boolean; findings_count: number; mission: string; failed: string[]; message: string }

function parseFlags(argv: string[]): { stage?: string; outputPath?: string } {
  const out: { stage?: string; outputPath?: string } = {};
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === "--stage") out.stage = argv[++i];
    else if (argv[i] === "--output-path") out.outputPath = argv[++i];
  }
  return out;
}

function emit(r: Result): never {
  process.stdout.write(`${JSON.stringify(r)}\n`);
  process.exit(0);
}

const passThrough = (): never =>
  emit({ pass: true, findings_count: 0, mission: "", failed: [], message: "not a video mission check file" });

export function evaluate(raw: string, mission: string): Result {
  let parsed: { mission?: string; checks?: Check[] };
  try {
    parsed = JSON.parse(raw);
  } catch (e) {
    return { pass: false, findings_count: 1, mission, failed: ["parse"], message: `check JSON is not valid JSON: ${e instanceof Error ? e.message : String(e)}` };
  }
  const checks = Array.isArray(parsed.checks) ? parsed.checks : [];
  if (checks.length === 0) {
    return { pass: false, findings_count: 1, mission, failed: ["no-checks"], message: "check JSON has no checks: the mission was not measured" };
  }
  const failed = checks.filter((c) => c.pass !== true).map((c) => `${c.label ?? c.id ?? "?"}: ${JSON.stringify(c.value)} (target ${JSON.stringify(c.target)})`);
  const name = parsed.mission ?? mission;
  return failed.length === 0
    ? { pass: true, findings_count: 0, mission: name, failed: [], message: `${name}: all ${checks.length} checks passed` }
    : { pass: false, findings_count: failed.length, mission: name, failed, message: `${name}: ${failed.length}/${checks.length} checks failed` };
}

export function main(argv: string[]): void {
  const flags = parseFlags(argv);
  if (!flags.outputPath) {
    process.stderr.write("aidlc-sensor-video-mission-check: --output-path is required\n");
    process.exit(1);
  }
  const file = basename(flags.outputPath);
  const isCheck = /^video-mission-[a-z]+-check\.json$/.test(file);
  const isSummary = /^video-mission-[a-z]+\.md$/.test(file);
  if (!isCheck && !isSummary) passThrough();

  // Fired on the summary: the stage's check JSON must exist beside it.
  const checkPath = isCheck ? flags.outputPath : join(dirname(flags.outputPath), file.replace(/\.md$/, "-check.json"));
  const mission = file.replace(/^video-mission-/, "").replace(/(-check)?\.(json|md)$/, "");
  if (!existsSync(checkPath)) {
    const near = existsSync(dirname(checkPath)) ? readdirSync(dirname(checkPath)).filter((f) => f.endsWith("-check.json")) : [];
    emit({ pass: false, findings_count: 1, mission, failed: ["missing-check"], message: `no ${basename(checkPath)} beside the summary (found: ${near.join(", ") || "none"}); run mission_check.py` });
  }
  emit(evaluate(readFileSync(checkPath, "utf-8"), mission));
}

if (import.meta.main) main(process.argv.slice(2));
