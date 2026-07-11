# Contract: `velmo.mlops` public Python API

Source of truth: `tests/acceptance/test_mlops.py` (never modified to make this pass — this
document restates it for design purposes only).

```python
from velmo.mlops import (
    DeliveryBlocked,
    Scores,
    current_version,
    enforce_threshold,
    run_eval,
    write_report,
)
```

## `run_eval(agent: Evaluable) -> Scores`

- Runs the memory, guardrails, and quality suites against `agent` (see data-model.md for
  what `agent` must expose).
- Internally repeats each suite 3× and averages + snaps to a 0.02 grid (research.md §1) —
  callers never see individual run noise.
- Returns a `Scores` with all eight fields populated, each `memory`/`guardrails`/`quality`/
  `global_` in `[0.0, 1.0]`.
- Raises `EvalDataError` (uncaught) if any of the three `eval/*.jsonl` inputs is missing,
  empty, or contains a line that fails to parse as JSON — this is intentional fail-closed
  behavior (FR-010), not a bug to swallow.

## `enforce_threshold(scores: Scores, threshold: float) -> None`

- Raises `DeliveryBlocked` iff `scores.global_ < threshold`. Strict `<` — a score exactly
  equal to `threshold` does **not** raise.
- Returns `None` (no value) on pass.

## `current_version() -> str`

- Returns a non-empty, deterministic id derived from `SYSTEM_PROMPT` + default
  `MemoryManager` config + default `GuardrailEngine` config (data-model.md).
- Takes no arguments — it describes "the version currently checked into the repo," not a
  specific `agent` instance passed elsewhere.

## `write_report(scores: Scores, path: Path) -> None`

- Writes/overwrites a Markdown file at `path`.
- The file's lowercased text MUST contain the literal unaccented substrings: `"memoire"`,
  `"blocage"`, `"faux positif"`, `"latence"`, `"cout"` (no `é`/`û`/etc. on those specific
  words — the acceptance test checks byte-for-byte substrings after `.lower()`, and an
  accented character does not match its unaccented counterpart).
- Creates parent directories of `path` if they do not exist.

## `DeliveryBlocked(Exception)`

- Raised only by `enforce_threshold`. Carries a human-readable message (e.g. including the
  actual score and threshold) for CI log output.
