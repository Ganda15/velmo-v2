# Feature Specification: Quality Evaluation Loop

**Feature Branch**: `001-quality-eval-loop`

**Created**: 2026-07-11

**Status**: Draft

**Input**: User description: "Velmo 2.2 must prove non-regression at every version through
three evaluation suites and a blocking CI gate. Acceptance criteria (from the trainer's
brief): (1) Given the three suites, when the evaluation runs, then a global score plus
memory / guardrails / quality sub-scores are produced and versioned. (2) Given a regression
(long-term memory disabled, or a guardrail removed), when the CI runs, then the score drops
and delivery is blocked. (3) Given a run, when mlops/report.md is opened, then it shows
memory score, blocking rate, false-positive rate, latency, and cost. Evaluation inputs:
memory_cases.jsonl and guardrail_cases.jsonl. A 'version' of the agent = prompt + memory
config + guardrail config."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Produce a versioned score from the three suites (Priority: P1)

Every time the agent's prompt, memory configuration, or guardrail configuration changes,
someone needs a single trustworthy answer to "did this make the agent worse?" — computed
automatically from the three evaluation suites (memory, guardrails, quality) and tied to
the exact version that produced it.

**Why this priority**: Nothing else in this feature — the CI gate, the report — has data
to act on without this. It is the foundation, and on its own already proves that automated,
repeatable model testing exists (RNCP C12).

**Independent Test**: Trigger the evaluation suites against a known agent version and
confirm a global score plus the three sub-scores (memory, guardrails, quality) are produced
and recorded against that exact version — independent of whether CI blocking or reporting
exist yet.

**Acceptance Scenarios**:

1. **Given** the three evaluation suites (memory, guardrails, quality) and a defined agent
   version (prompt + memory config + guardrail config), **When** the evaluation runs,
   **Then** a global score and the three sub-scores (memory, guardrails, quality) are
   produced and stored, tied to that version.
2. **Given** two different agent versions evaluated at different times, **When** their
   scores are recorded, **Then** each score is unambiguously attributable to its own
   version, with no overwriting or ambiguity between runs.
3. **Given** `memory_cases.jsonl` and `guardrail_cases.jsonl` as the evaluation inputs,
   **When** the evaluation runs, **Then** every case in both files is exercised and
   contributes to its corresponding sub-score.

---

### User Story 2 - CI blocks delivery on regression (Priority: P1)

When a change regresses the agent — for example long-term memory gets disabled, or a
guardrail is accidentally removed — delivery must stop automatically. Nobody should have
to remember to check the score by hand before merging or shipping.

**Why this priority**: This is the actual quality gate the trainer's brief and the project
constitution require. Scoring without enforcement would not prove anything; this is what
turns User Story 1's data into a real safeguard (RNCP C13).

**Independent Test**: Deliberately introduce a known regression (disable long-term memory,
or remove a guardrail) on a change intended for delivery, run CI, and confirm the run is
blocked with a visibly lower score than the last passing baseline.

**Acceptance Scenarios**:

1. **Given** a regression that disables long-term memory, **When** CI runs the evaluation,
   **Then** the memory sub-score (and therefore the global score) drops and the CI run is
   blocked, preventing delivery.
2. **Given** a regression that removes a guardrail, **When** CI runs the evaluation,
   **Then** the guardrails sub-score (and therefore the global score) drops and the CI run
   is blocked, preventing delivery.
3. **Given** an agent version with no regression relative to the last passing baseline,
   **When** CI runs the evaluation, **Then** the score remains at or above the delivery
   threshold and CI does not block delivery.

---

### User Story 3 - `mlops/report.md` surfaces the run's signals (Priority: P2)

After an evaluation run, Era (or the jury) can open `mlops/report.md` and read, in plain
terms, what happened: how good is memory, how often are guardrails firing, how often are
they wrong, and what it cost — without digging through CI logs or code.

**Why this priority**: Builds directly on User Story 1's data and proves RNCP C20
(application monitoring signals). It does not depend on User Story 2's blocking logic, so
it can be delivered and demoed independently of the gate itself.

**Independent Test**: Run an evaluation, open `mlops/report.md`, and verify it shows the
memory score, blocking rate, false-positive rate, latency, and cost for that run.

**Acceptance Scenarios**:

1. **Given** a completed evaluation run, **When** `mlops/report.md` is opened, **Then** it
   shows the memory score, the guardrail blocking rate, the guardrail false-positive rate,
   latency, and cost for that run.
2. **Given** a new evaluation run following a previous one, **When** `mlops/report.md` is
   regenerated, **Then** it reflects the latest run's signals, not stale data from a prior
   version.

---

### Edge Cases

- What happens when `memory_cases.jsonl` or `guardrail_cases.jsonl` is missing, empty, or
  malformed? The evaluation MUST fail loudly and block, not silently produce a misleadingly
  high score.
- What happens when the global score lands exactly at the threshold — is "at threshold" a
  pass or a block? The rule MUST be documented and unambiguous.
- What happens when the evaluation run itself crashes or times out partway through (e.g., an
  LLM call fails)? CI MUST fail closed — block delivery — rather than fail open.
- What happens when two CI runs for different changes execute concurrently? Their scores and
  versions MUST stay distinct, with no cross-contamination between runs.
- What happens when an evaluation case itself references data belonging to a specific
  simulated customer? Evaluation fixtures MUST still respect per-user isolation, the same as
  production data.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST run three evaluation suites — memory, guardrails, and quality
  — against a given agent version, where an agent version is defined as the combination of
  prompt + memory configuration + guardrail configuration.
- **FR-002**: The system MUST compute a memory sub-score by replaying every case in
  `memory_cases.jsonl`.
- **FR-003**: The system MUST compute a guardrails sub-score consisting of at least a
  blocking rate and a false-positive rate, derived from every case in
  `guardrail_cases.jsonl`.
- **FR-004**: The system MUST compute a quality sub-score reflecting the overall correctness
  of the agent's responses.
- **FR-005**: The system MUST combine the three sub-scores into a single global score using
  a documented, versioned formula; the formula MAY change over time, but each change MUST be
  recorded.
- **FR-006**: The system MUST persist each evaluation run's global score, sub-scores, and
  the exact agent version it was computed against, so every result is traceable to a
  specific version.
- **FR-007**: The system MUST run the evaluation automatically as part of CI on every change
  intended for delivery.
- **FR-008**: The system MUST block delivery (fail the CI run) whenever the global score for
  the version under test falls below the documented threshold.
- **FR-009**: The system MUST NOT block delivery when the global score is at or above the
  documented threshold (no false-positive blocking of healthy versions).
- **FR-010**: The system MUST fail closed — a crashed, timed-out, or otherwise incomplete
  evaluation run MUST block delivery rather than being treated as a pass.
- **FR-011**: The system MUST generate or update `mlops/report.md` after each run, showing
  at minimum: memory score, guardrail blocking rate, guardrail false-positive rate, latency,
  and cost.
- **FR-012**: The report MUST reflect the most recent run and MUST NOT silently retain stale
  signals from a previous agent version.
- **FR-013**: The system MUST keep evaluation fixtures and any evaluation-time customer data
  isolated per simulated user, consistent with the project's per-user isolation requirement.
- **FR-014**: The system MUST NOT require modification of the evaluation case files
  (`memory_cases.jsonl`, `guardrail_cases.jsonl`) themselves to pass — the suites are the
  contract for what "no regression" means.

### Key Entities *(include if feature involves data)*

- **Agent Version**: the unit being evaluated — the combination of prompt, memory
  configuration, and guardrail configuration; has an identifier and is what every score is
  attributed to.
- **Evaluation Run**: one execution of the three suites against one agent version; has a
  timestamp, the agent version it targeted, and its resulting scores.
- **Global Score**: the single combined pass/fail number for a run, computed from the three
  sub-scores per the documented formula.
- **Memory Sub-Score**: result of replaying `memory_cases.jsonl` against the agent version.
- **Guardrail Sub-Score**: blocking rate + false-positive rate from replaying
  `guardrail_cases.jsonl`.
- **Quality Sub-Score**: the third component of the global score.
- **Evaluation Case**: one row from `memory_cases.jsonl` or `guardrail_cases.jsonl` — an
  input plus its expected outcome.
- **Report**: the human-readable `mlops/report.md`, summarizing the most recent run's
  signals (memory score, blocking rate, false-positive rate, latency, cost).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of CI runs on a delivery-intended change produce a global score plus the
  three sub-scores, attributable to a specific, identifiable agent version.
- **SC-002**: When a known regression is introduced (memory disabled or a guardrail
  removed), the CI run is blocked in 100% of attempts, with the drop visible in the
  corresponding sub-score.
- **SC-003**: When no regression is present relative to the last passing baseline, the CI
  run is not blocked in 100% of attempts (zero false-positive blocks across repeated
  identical runs).
- **SC-004**: After any evaluation run, a reader can find the memory score, blocking rate,
  false-positive rate, latency, and cost in `mlops/report.md` without reading source code or
  CI logs.
- **SC-005**: Given any past evaluation score, its exact agent version (prompt + memory
  config + guardrail config) can be identified with no ambiguity.

## RNCP Traceability

Per the project constitution (Principle V), this feature states which criteria it proves:

- **C12** (automated model tests) — via User Story 1: three evaluation suites run
  automatically and produce versioned scores.
- **C13** (continuous delivery gate) — via User Story 2: CI blocks delivery when the global
  score drops below the documented threshold.
- **C20** (application monitoring signals) — via User Story 3: `mlops/report.md` surfaces
  memory score, blocking rate, false-positive rate, latency, and cost.

## Assumptions

- The exact numeric threshold for the global score, the weighting formula between the three
  sub-scores, and the anti-flakiness strategy (how non-deterministic LLM output is smoothed
  so identical versions yield identical gate outcomes) are not yet finalized. Per
  `docs/chantier3/JOURNAL.md` (Étape 2), these remain pending formateur validation and MUST
  be documented and versioned before the CI gate (Étape 6) ships. This spec requires that
  such a threshold and formula exist and be documented (FR-005, FR-008) without prescribing
  their exact values.
- The "quality" sub-score's scope follows whatever case set the project's `eval/` directory
  defines for it; this spec does not redefine what "quality" measures.
- "CI" in the acceptance criteria refers to the project's existing GitHub Actions pipeline
  (`quality.yml`, per the constitution), not a new CI system.
- Cost and latency signals in the report are per-run aggregates, not per-case breakdowns,
  unless a future feature requests finer granularity.
- This feature covers the evaluation/scoring/gating/reporting loop itself; authoring the
  individual case content inside `memory_cases.jsonl` / `guardrail_cases.jsonl` is
  implementation-task scope, not spec scope.
