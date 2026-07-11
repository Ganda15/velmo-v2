# Phase 1 Data Model: Quality Evaluation Loop

All entities below are in-process Python objects (dataclasses/plain values) — there is no new
persistent storage; `Scores` is computed fresh on each `run_eval()` call and only ever
persisted as the rendered `mlops/report.md` file (and, transiently, CI logs/exit code).

## Scores (existing — `src/velmo/mlops/__init__.py`)

Already defined, frozen dataclass; this feature fills in *how* each field is computed, not
its shape (shape is fixed by `tests/acceptance/test_mlops.py`):

| Field | Type | Meaning | Range |
|---|---|---|---|
| `memory` | `float` | Memory sub-score (§ Memory Suite) | `0.0–1.0` |
| `guardrails` | `float` | Guardrails sub-score (§ Guardrail Suite) | `0.0–1.0` |
| `quality` | `float` | Quality sub-score (§ Quality Suite) | `0.0–1.0` |
| `global_` | `float` | Weighted combination, capped to `0.0` on a serious guardrail leak | `0.0–1.0` |
| `block_rate` | `float` | Of guardrail cases expecting a block, fraction actually blocked | `0.0–1.0` |
| `false_positive_rate` | `float` | Of guardrail cases expecting allow, fraction wrongly blocked | `0.0–1.0` |
| `latency_ms` | `float` | Mean wall-clock time per agent call across the run | `≥ 0` |
| `cost` | `float` | Estimated cost (`calls * EVAL_COST_PER_CALL`, see research.md §5) | `≥ 0` |

Note: `guardrails` (the weighting sub-score) is distinct from `block_rate` /
`false_positive_rate` (the two raw signals surfaced in the report) — see Guardrail Suite
below for how one derives from the other.

## AgentVersion (conceptual — not a stored row, a hash)

Not a class; `current_version() -> str` computes it on demand from three sources of truth
already in the codebase:

- **prompt**: `velmo.agent.SYSTEM_PROMPT`
- **memory config**: default `MemoryManager()` constructor parameters (currently just
  `token_budget`)
- **guardrail config**: `GuardrailEngine.CATEGORIES` + `GuardrailEngine.INPUT_KEYWORDS`

These are serialized to a stable JSON structure (`sort_keys=True`), SHA-256 hashed, and
truncated: `f"v-{digest[:12]}"`. Two calls with unchanged prompt/memory/guardrail config
always produce the same id; changing any of the three changes it. Never empty.

## Evaluation Case (existing files, read-only)

Three JSONL files under `eval/`, never modified by this feature (FR-014):

- **Memory case** (`eval/memory_cases.jsonl`, 12 rows): `id`, `tag`, `user_id`, `turns`
  (list of `{role, content}`), `evaluation: {type, question, expected_substring}`.
- **Guardrail case** (`eval/guardrail_cases.jsonl`, 35 rows): `id`, `user_id`, `message`,
  `category` (one of `hate`, `violence`, `sexual`, `pii`, `secret_leak`, `out_of_scope`,
  `prompt_injection`, `legitimate`), `expected_action` (`"block"` | `"allow"`), `where`
  (`"input"` | `"output"`).
- **Quality case** (`eval/quality_cases.jsonl`, 8 rows): `id`, `user_id`, `question`,
  `expected_substring`.

Loading is centralized in one loader (`src/velmo/mlops/cases.py`) shared by all three suite
runners. Missing file, empty file, or a line that fails `json.loads` raises `EvalDataError`
(a new, narrow exception) — uncaught, this propagates out of `run_eval()` and, in the CLI,
crashes the process with a non-zero exit code (fail-closed, FR-010).

## Evaluable agent (duck-typed, not a new class)

`run_eval(agent)` accepts anything exposing:
- `respond(user_id: str, message: str) -> str` (existing `Evaluable` protocol)
- `guardrails` — an object with `check_input(message) -> Decision` and
  `check_output(text) -> Decision` (see research.md §3 for why this is required beyond the
  formal `Evaluable` protocol)

Both `tests/conftest.build_reference_agent()` / `build_degraded_agent()` and the new
`src/velmo/mlops` `build_eval_agent()` satisfy this by construction (they return real
`velmo.agent.Agent` instances).

## Suite results (internal, not exported)

Intermediate dataclasses local to each suite module — not part of the public contract, so
free to change without breaking `tests/acceptance/test_mlops.py`:

- `MemorySuiteResult(score: float, total: int, passed: int)`
- `GuardrailSuiteResult(score: float, block_rate: float, false_positive_rate: float, serious_leak: bool)`
- `QualitySuiteResult(score: float, total: int, passed: int)`

`scoring.py` consumes one of each (already averaged over 3 runs per research.md §1) and
produces the final `Scores`.

## Report (generated file, not a class)

`write_report(scores, path)` renders Markdown containing, at minimum, the labels (unaccented,
per the acceptance test): `memoire`, `blocage`, `faux positif`, `latence`, `cout`, each
followed by its corresponding `Scores` value, plus the version id from `current_version()`
and a timestamp. Overwrites `path` fully on each call (FR-012 — no stale data merge).
