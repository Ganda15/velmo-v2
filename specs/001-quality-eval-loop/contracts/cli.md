# Contract: `python -m velmo.mlops.score` CLI

Consumed by `.github/workflows/quality.yml`'s commented-out gate step:

```yaml
- name: Quality gate
  run: uv run python -m velmo.mlops.score --min-score 0.8
```

This feature must make that step work by uncommenting it — the workflow file itself is not
redesigned.

## Invocation

```bash
python -m velmo.mlops.score [--min-score FLOAT] [--report PATH]
```

- `--min-score` (optional): defaults to `EVAL_MIN_SCORE` from the environment (`.env`), which
  defaults to `0.8` if unset. Passed straight to `enforce_threshold`.
- `--report` (optional): defaults to `mlops/report.md` at the repository root (research.md
  §4). Passed straight to `write_report`.

## Behavior

1. Build the evaluated agent via `build_eval_agent()` (SQLite-only, no Docker — research.md
   §6).
2. `scores = run_eval(agent)`.
3. `write_report(scores, report_path)` — **always**, even if the run is about to be blocked,
   so the report explains *why* it was blocked.
4. `enforce_threshold(scores, min_score)`:
   - Pass → print a one-line summary (`global_`, `current_version()`) to stdout, exit code
     `0`.
   - `DeliveryBlocked` → print the reason to stderr, exit code `1`.
5. Any other exception (e.g. `EvalDataError` from a malformed `eval/*.jsonl`) is **not**
   caught — it propagates, Python's default traceback goes to stderr, exit code is non-zero.
   This is deliberate fail-closed behavior (FR-010): a broken evaluation run must never look
   like a passing CI job.

## CI integration

No changes to `.github/workflows/quality.yml` beyond removing the four leading `# `
characters on the existing commented step — the command, working directory (`uv run`
executes from the repo checkout root), and dependencies (`uv sync`, already run by an earlier
step) are all already correct for this contract.
