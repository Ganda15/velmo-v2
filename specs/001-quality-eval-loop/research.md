# Phase 0 Research: Quality Evaluation Loop

All items below were open design questions not fully pinned by
`docs/chantier3/DOSSIER-CONCEPTION.md` or by the acceptance test contract
(`tests/acceptance/test_mlops.py`). Each is resolved here so Phase 1 design has no
remaining ambiguity.

## 1. Anti-noise averaging mechanism (dossier §2.3: "moyenne sur 3 exécutions + tolérance ± 2 points")

**Decision**: Run each of the three suites 3 times per `run_eval(agent)` call. Average each
sub-score across the 3 runs, then snap the averaged value to the nearest 0.02 (i.e.
`round(mean / 0.02) * 0.02`, clamped to `[0.0, 1.0]`) before it becomes part of `Scores`.
`enforce_threshold` itself stays a plain `scores.global_ < threshold` comparison — no
tolerance logic there.

**Rationale**: The acceptance contract is explicit and literal: *"exactly at threshold =
pass"* — i.e. `enforce_threshold` must be a simple `<` comparison, so the ± 0.02 tolerance
cannot live there without contradicting the contract. Moving the tolerance into score
computation (snap-to-grid after averaging) is what actually delivers the dossier's stated
goal — "une version identique donne toujours le même verdict" — because two evaluations of
an unchanged agent that differ only by ≤ 0.02 due to LLM noise land on the same grid point
and therefore the same pass/fail outcome.

**Alternatives considered**:
- *Widen the pass band inside `enforce_threshold`* (e.g. `< threshold - 0.02`): rejected,
  contradicts the "exactly at threshold = pass" contract clause.
- *Median of 3 runs instead of mean*: rejected as unnecessary complexity for 3 samples;
  mean is simpler and sufficient given the small sample size.

## 2. Guardrail-leak severity classification (dossier §2.2: "un garde-fou grave... plafonne à 0")

**Decision**: The categories `hate`, `violence`, `sexual`, `pii`, `secret_leak` are
"serious." If any evaluation case whose `category` is in that set has
`expected_action == "block"` but the guardrail engine under test allows it through, the run's
`global_` is hard-capped to `0.0`, overriding the weighted average entirely.
`out_of_scope` and `prompt_injection` leaks are not in the serious set — they still count
against the ordinary guardrails sub-score, but do not trigger the hard cap.

**Rationale**: This is a literal restatement of the dossier's own wording, which names
exactly those five categories. No re-decision needed; recorded here only so the
implementation has an explicit, testable list rather than re-deriving it from prose each
time.

**Alternatives considered**: none — this is an already-ratified design decision, not an open
question; only the source-of-truth list needed to be pinned to code.

## 3. How the guardrail suite observes block/allow decisions

**Decision**: The guardrail suite calls `agent.guardrails.check_input(message)` (or
`check_output` when a case's `where` is `"output"`) directly on the `agent.guardrails`
component, rather than inferring block/allow from `agent.respond(...)`'s returned string.

**Rationale**: `tests/conftest.py`'s `build_reference_agent()` / `build_degraded_agent()`
both return real `Agent` instances whose `.guardrails` attribute is swapped between
`GuardrailEngine` (reference) and `AllowAllGuardrails` (degraded) — that swap *is* the
regression the acceptance test exercises. Calling the guardrail component directly gives an
unambiguous `Decision(allowed, category, ...)` per case instead of pattern-matching refusal
text, which would be fragile and would silently break if refusal wording changes.
This does widen the informal `Evaluable` protocol beyond `.respond(...)` to include
`.guardrails` — acceptable because every real caller (both conftest fixtures and the
production `Agent` class) already provides it; documented in `data-model.md`.

**Alternatives considered**:
- *Infer block/allow from the agent's final answer text*: rejected as fragile (couples the
  evaluator to exact refusal strings) and it cannot distinguish "blocked" from "the LLM
  happened to produce a similar-looking answer."

## 4. Report output path

**Decision**: `python -m velmo.mlops.score` defaults to writing the report to
`mlops/report.md` at the **repository root** (a generated-artifact directory, distinct from
the `src/velmo/mlops/` source package). `write_report(scores, path)` itself takes an
explicit `path` and has no opinion on location — the default lives only in the CLI.

**Rationale**: Every prose reference in the constitution, spec, and journal
(`Exposer les signaux dans mlops/report.md`) writes the path without a `src/velmo/` prefix,
and a top-level `mlops/` output directory keeps generated reports out of the installable
package. `write_report` staying path-agnostic keeps the acceptance test
(`write_report(scores, tmp_path / "report.md")`) trivially satisfiable regardless of this
default.

**Alternatives considered**:
- *`src/velmo/mlops/report.md`*: rejected — mixes a generated artifact into the source
  package the same directory `__init__.py` etc. live in, and would ship the last run's
  report inside the built wheel.

## 5. Cost signal without token-usage data

**Decision**: `cost` is a simple per-call estimate: `num_llm_calls * EVAL_COST_PER_CALL`
(env var, default `0.0`), not a real token-metered figure.

**Rationale**: `velmo.llm.LLM.invoke()` returns a plain string with no usage/token metadata,
and extending that interface is out of scope for this feature ("keep minimal — no framework
beyond what pyproject.toml already declares," and the spec's Assumptions already scope cost
signals as per-run aggregates without committing to a specific accounting method). The
report only needs to *show* a cost signal (FR-011); the acceptance test checks for the
substring `"cout"`, not a specific value.

**Alternatives considered**:
- *Wire real Azure token usage through*: rejected for this feature — would require changing
  the stable `LLM` protocol, which several other components depend on; flagged as a
  reasonable follow-up feature, not part of this plan.

## 6. Building the "current" evaluated agent for the CLI

**Decision**: Add `build_eval_agent()` inside `src/velmo/mlops/` (not in `tests/conftest.py`,
which the CLI must not import) that mirrors `conftest.build_reference_agent()`: a fresh
seeded SQLite session (`db.fresh_sqlite_session()` + `sampledata.seed()`), `LocalKB()`,
`GuardrailEngine()`, `MemoryManager()` — but uses `llm.get_llm()` (real Kimi/Azure client
when credentials are configured, `EchoLLM` fallback otherwise) instead of hardcoding
`EchoLLM`.

**Rationale**: Satisfies the constitution's "evaluation MUST run in dev using SQLite only —
no Docker required locally" without ever touching `DB_URL`/Postgres or `CHROMA_URL`/Chroma,
while still using the imposed Kimi/Azure LLM when secrets are present (e.g. in CI, if
configured) rather than silently forcing the echo fallback. It duplicates a small amount of
fixture-building logic from `tests/conftest.py`, but `src/` cannot import from `tests/` in
production code, and the tests' `build_reference_agent()` intentionally hardcodes `EchoLLM`
for determinism — the CLI's needs are close but not identical.

**Alternatives considered**:
- *Import `tests/conftest.py` from `src/velmo/mlops/score.py`*: rejected — production code
  importing from the test tree is backwards and would break `pip install`/wheel builds that
  don't ship `tests/`.

## Constitution discrepancy flagged (not resolved here)

The ratified constitution (`.specify/memory/constitution.md`, Principle I) names the
production database URL environment variable as `MEMORY_DB_URL`. The actual repo
(`.env.example`, `src/velmo/db.py:168`) uses `DB_URL`. This plan follows the **real code**
(`DB_URL`) since that is what `run_eval`/`build_eval_agent` must actually read, but this is a
documentation defect in the constitution, not a design decision of this feature. Recorded
here rather than silently "corrected" in the constitution, per instruction — Era should
ratify a PATCH-level constitution amendment (wording fix, not a principle change) separately.
