# Implementation Plan: Quality Evaluation Loop

**Branch**: `001-quality-eval-loop` | **Date**: 2026-07-12 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-quality-eval-loop/spec.md`

## Summary

Deliver the `velmo.mlops` package that turns three evaluation suites (memory, guardrails,
quality) into one versioned global score, blocks CI delivery below a documented threshold,
and writes a human-readable `mlops/report.md`. The public API, its exact signatures, the
scoring scale, and the CI hook it plugs into are all already fixed by
`tests/acceptance/test_mlops.py` and `.github/workflows/quality.yml` — this plan is about
*how* to implement against that existing, non-negotiable contract, using only what
`pyproject.toml` already declares (stdlib `json`/`hashlib`/`statistics`/`argparse` plus the
project's existing SQLAlchemy/dotenv stack), reusing `eval/*.jsonl` as-is.

## Technical Context

**Language/Version**: Python 3.11 (`pyproject.toml` `requires-python = ">=3.11,<3.12"`)

**Primary Dependencies**: none new. Stdlib only (`json`, `hashlib`, `statistics`, `argparse`,
`time`, `pathlib`, `dataclasses`) plus already-declared project deps consumed transitively
through `velmo.agent`/`velmo.db`/`velmo.llm`/`velmo.kb_store` (`sqlalchemy`, `python-dotenv`;
`langchain-azure-ai`/`chromadb` only if those optional extras are installed and their env
vars set — otherwise the existing `EchoLLM`/`LocalKB` offline fallbacks are used untouched).

**Storage**: SQLite in memory only, via the existing `db.fresh_sqlite_session()` — no
Postgres/`DB_URL` and no Chroma/`CHROMA_URL` touched by this feature (constitution: "evaluation
MUST run in dev using SQLite only — no Docker required locally").

**Testing**: pytest (already a dev dependency); contract is
`tests/acceptance/test_mlops.py`, fixtures from `tests/conftest.py`
(`build_reference_agent`, `build_degraded_agent`, both pre-existing and unmodified by this
feature).

**Target Platform**: GitHub Actions `ubuntu-latest` (CI, per `.github/workflows/quality.yml`)
and Era's Windows dev machine (local `pytest`/AppLocker fallback per `CLAUDE.md`). No OS
-specific code needed — pure Python + stdlib + SQLite.

**Project Type**: Single project — new subpackage inside the existing `src/velmo/` tree plus
one generated-artifact directory (`mlops/` at repo root, output only, not a package).

**Performance Goals**: Not a performance-sensitive feature. The full evaluation (12 memory +
35 guardrail + 8 quality cases, each ×3 for anti-noise averaging = 165 agent interactions) must
complete comfortably inside a CI job's normal time budget; with the offline `EchoLLM`/`LocalKB`
fallbacks this is sub-second, and even against a real Azure/Kimi endpoint it stays well under
typical CI step timeouts.

**Constraints**: Must not modify `tests/acceptance/test_mlops.py`, `tests/conftest.py`'s two
builder functions, or any `eval/*.jsonl` file (constitution Principle II — the tests are the
contract). Must not add a new dependency to `pyproject.toml`. Must fail closed: a crashed or
malformed-input run must never produce a passing report or a zero exit code (FR-010).

**Scale/Scope**: Single-agent, single-machine evaluation runs; not designed for concurrent
multi-agent load testing or historical score storage beyond what a single `mlops/report.md`
holds per run (SC-005's "traceable to a version" is satisfied via `current_version()` +
report content, not a database of historical runs — no such store is requested by the spec).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Check | Status |
|---|---|---|
| I. Imposed Technology Stack | No LLM/DB/vector-store substitution; SQLite path uses the existing `db.fresh_sqlite_session()`, Kimi/Azure reached only through the existing `llm.get_llm()` | ✅ Pass |
| I. (documentation defect) | Constitution text says `MEMORY_DB_URL`; real repo uses `DB_URL` (`.env.example`, `db.py:168`) | ⚠️ Flagged in research.md — plan follows the real code (`DB_URL`); constitution needs a separate PATCH-level wording fix, out of this plan's scope |
| II. TDD Is the Contract | `tests/acceptance/test_mlops.py` and `tests/conftest.py`'s two builders are read-only inputs to this plan, never edited | ✅ Pass |
| III. GDPR by Design (R3/R5) | Eval fixtures use existing per-user-scoped `MemoryManager`; each run gets a fresh SQLite session (no cross-run/cross-user bleed); this feature adds no new customer-data storage, so no new right-to-be-forgotten surface is introduced | ✅ Pass |
| IV. Quality Gate Blocks Delivery | `enforce_threshold` + `score.py` CLI + uncommenting the existing `quality.yml` step is exactly this gate, automatic in CI | ✅ Pass |
| V. RNCP Traceability | Already stated in spec.md's RNCP Traceability section (C12/C13/C20); this plan implements exactly those three user stories, no scope drift | ✅ Pass |
| VI. Secrets & OWASP | No new endpoint introduced (CLI + library, no HTTP surface); no secret is read beyond existing `EVAL_MIN_SCORE`/`AZURE_AI_INFERENCE_*` env vars already in `.env.example`, never hardcoded | ✅ Pass |
| Quality & Evaluation Chain (Governance) | Reuses `eval/*.jsonl` as authoritative inputs; versions the agent config via `current_version()`; surfaces memory score, blocking rate, false-positive rate, latency, cost in `mlops/report.md` | ✅ Pass |

No unjustified violations — Complexity Tracking table below is empty by design.

## Project Structure

### Documentation (this feature)

```text
specs/001-quality-eval-loop/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md         # Phase 1 output
├── quickstart.md         # Phase 1 output
├── contracts/
│   ├── python-api.md     # velmo.mlops public API contract
│   └── cli.md            # `python -m velmo.mlops.score` CLI contract
└── tasks.md              # Phase 2 output (/speckit-tasks — not created by this command)
```

### Source Code (repository root)

```text
src/velmo/mlops/
├── __init__.py          # Public API surface (existing file — fill in bodies, keep signatures
│                         #   and the Scores/DeliveryBlocked/Evaluable already defined there)
├── cases.py              # NEW — shared JSONL loader for the 3 eval/*.jsonl files; raises
│                         #   EvalDataError on missing/empty/malformed input (fail-closed)
├── suites/
│   ├── __init__.py       # NEW
│   ├── memory_suite.py    # NEW — replays eval/memory_cases.jsonl -> MemorySuiteResult
│   ├── guardrail_suite.py # NEW — replays eval/guardrail_cases.jsonl -> GuardrailSuiteResult
│   └── quality_suite.py   # NEW — replays eval/quality_cases.jsonl -> QualitySuiteResult
├── scoring.py             # NEW — 3-run averaging + 0.02 grid snap + weighting (35/35/30) +
│                         #   serious-guardrail-leak hard cap to 0.0 -> Scores
├── versioning.py          # NEW — current_version(): hash(prompt + memory config +
│                         #   guardrail config) -> short version id
├── report.py              # NEW — write_report(): unaccented-French Markdown renderer
├── eval_agent.py           # NEW — build_eval_agent(): SQLite-only, get_llm()-backed agent
│                         #   for the CLI (mirrors conftest's builders, does not import them)
└── score.py                # NEW — `python -m velmo.mlops.score` CLI entry point

mlops/                    # NEW, repo root — generated artifact directory (git-ignored
│                         #   contents except a placeholder), holds report.md after each run

.github/workflows/quality.yml   # EDIT — uncomment the existing "Quality gate" step only
```

**Structure Decision**: Single project (this repo is already a single `src/velmo` package,
no frontend/backend split). All new code lives under the existing `src/velmo/mlops/`
subpackage next to the other already-stubbed subsystems (`memory/`, `guardrails/`), following
the same pattern: a stable `__init__.py` surface backed by small, focused internal modules.
The only new top-level directory is `mlops/` at the repo root, which holds a *generated*
artifact (`report.md`), not source code, and is therefore kept separate from
`src/velmo/mlops/` (research.md §4).

## Complexity Tracking

*(empty — no Constitution Check violation requires justification; see table above)*
