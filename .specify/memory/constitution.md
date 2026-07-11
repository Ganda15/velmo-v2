<!--
Sync Impact Report
- Version change: [TEMPLATE] → 1.0.0 (initial ratification)
- Modified principles: n/a (all six principles newly defined from placeholders)
- Added sections:
  - Core Principles I–VI (Imposed Technology Stack; Test-First — Acceptance Tests Are
    the Contract; GDPR by Design — Isolation & Right to Be Forgotten; Quality Gate
    Blocks Delivery; RNCP Traceability; Secrets & OWASP API Security)
  - Development Workflow (Section 2)
  - Quality & Evaluation Chain (Section 3)
  - Governance (amendment procedure, versioning policy, compliance review)
- Removed sections: none (template placeholders replaced, no prior content existed)
- Templates requiring updates:
  - .specify/templates/plan-template.md ✅ no change needed (Constitution Check gate
    already reads dynamically from this file)
  - .specify/templates/spec-template.md ✅ no change needed (no constitution-specific
    placeholders)
  - .specify/templates/tasks-template.md ✅ no change needed (no constitution-specific
    placeholders)
  - README.md ✅ consistent (stack description already matches Principle I)
  - CLAUDE.md ✅ consistent (stack/TDD/RNCP rules already match Principles I, II, V)
- Follow-up TODOs: none — no placeholder left undefined
-->

# Velmo 2.2 Constitution

## Core Principles

### I. Imposed Technology Stack (NON-NEGOTIABLE)

The technology stack is fixed by the trainer's brief and MUST NOT be substituted,
swapped, or "improved" without explicit written sign-off from the trainer:

- **LLM**: Kimi, accessed via Azure AI. No other model provider or local model may
  replace it in any code path that reaches production or acceptance tests.
- **Long-term memory**: SQLite in development; PostgreSQL in production, selected
  exclusively via the `MEMORY_DB_URL` environment variable. No other database engine.
- **Vector store**: Chroma. No other vector database or in-house vector index.

Rationale: this is an RNCP-assessed exercise built on a formateur-defined brief; the
stack choice is itself part of what is being evaluated, and substituting components
invalidates the exercise regardless of technical merit.

### II. Test-First — Acceptance Tests Are the Contract (NON-NEGOTIABLE)

The acceptance test suites (`tests/acceptance/test_agent.py`,
`tests/acceptance/test_memory.py`, and any equivalent guardrail/quality suites) are
the contract for correct behavior. Implementation MUST be written to satisfy the
tests as given. Acceptance tests MUST NOT be edited, weakened, skipped, or deleted
in order to make them pass. New behavior MUST follow red→green TDD: write or
identify the failing test first, then implement the minimal code to pass it.

Rationale: the acceptance tests encode the formateur's specification; changing the
test to fit the code inverts the contract and destroys the value of TDD as
evidence of correctness for both Era and the jury.

### III. GDPR by Design — Isolation & Right to Be Forgotten (NON-NEGOTIABLE)

Every feature that touches customer data MUST implement, from its first version:

- **R3 — Per-user isolation**: one customer's data, memory, and conversation
  context MUST NEVER be readable, inferable, or leakable to another customer's
  session or query.
- **R5 — Right to be forgotten**: there MUST be a working, tested path to fully
  erase a given customer's stored data (memory, vector entries, logs where
  feasible) on request, and this path MUST be covered by a test before the
  feature is considered done.

Rationale: this is a customer-support agent handling real personal data (orders,
identity, purchase history); GDPR compliance is a legal and pedagogical
non-negotiable, not an optional hardening pass added later.

### IV. Quality Gate Blocks Delivery (NON-NEGOTIABLE)

A feature or change MUST NOT be delivered (merged, released, or presented as done)
if it causes the global evaluation score — computed from the memory, guardrail,
and quality evaluation suites — to drop below the threshold defined for the
project. This gate MUST be enforced automatically in CI (`quality.yml`); it MUST
NOT depend on a human remembering to check the score manually.

Rationale: Chantier 3's entire purpose is proving a CI-enforced, versioned quality
loop (C13); a gate that can be silently bypassed is not a gate.

### V. RNCP Traceability

Every feature, task, or spec written for this project MUST state explicitly which
RNCP37827 criterion or criteria (C1–C21) it is intended to demonstrate. This
mapping MUST appear in the spec/plan/task artifact for the feature (not only
after the fact in the journal), so that evidence can be traced from criterion →
requirement → code → test.

Rationale: the project's purpose is certification evidence; work that cannot be
traced to a criterion is out of scope for this exercise and should be flagged as
such rather than silently absorbed into the codebase.

### VI. Secrets & OWASP API Security (NON-NEGOTIABLE)

API keys, connection strings, and other secrets (Azure AI key, `MEMORY_DB_URL`
credentials, etc.) MUST live only in `.env` (or an equivalent untracked local
secret store) and MUST NEVER be committed to git, hardcoded, or logged. Every
HTTP-exposed endpoint MUST be evaluated against the OWASP API Security Top 10
(broken object-level authorization, broken authentication, excessive data
exposure, lack of rate limiting, etc.) before being considered complete, with
findings either fixed or explicitly and consciously accepted as a documented
risk.

Rationale: a support agent with tool access to order/refund data is a realistic
attack surface; treating security as an afterthought contradicts both the GDPR
principle (III) and standard professional practice expected at RNCP level.

## Development Workflow

- Era writes the implementation code herself. The assistant provides code and
  explanation in chat for review; code is only applied to the working tree on
  explicit instruction ("do it").
- Tests are run with the project virtual environment activated
  (`python -m pytest tests/acceptance/test_agent.py -v`,
  `python -m pytest tests/acceptance/test_memory.py -v`). If AppLocker blocks the
  venv interpreter, the documented fallback is
  `C:\Python314\python.exe -m pytest`.
- The Obsidian journal (`Projets/Velmo/JOURNAL-chantier3-evaluation-mlops.md`) and
  its in-repo mirror (`docs/chantier3/JOURNAL.md`) MUST be updated at each
  meaningful step, recording what changed, why, and what broke/passed.

## Quality & Evaluation Chain

- Three evaluation suites are authoritative: **memory** (replays
  `memory_cases.jsonl`), **guardrails** (blocking rate + false-positive rate on
  `guardrail_cases.jsonl`), and **quality** (produces the global score referenced
  in Principle IV).
- The agent version (prompt + memory config + guardrail config) MUST be versioned
  and the resulting score journaled alongside that version, so score changes can
  be attributed to a specific change.
- Signals — memory score, blocking rate, false-positive rate, latency, cost — MUST
  be surfaced in `mlops/report.md` in human-readable form, not only as raw CI
  output.

## Governance

This constitution supersedes ad hoc practice for this project; where CLAUDE.md,
chat instructions, or prior habits conflict with a principle above, the
constitution wins unless the trainer explicitly amends the brief.

**Amendment procedure**: amendments are made by editing this file, filling in a
Sync Impact Report as an HTML comment at the top of the file, and updating the
version per the policy below. Amendments that touch the imposed stack (Principle
I) or the acceptance-test contract (Principle II) require the trainer's explicit
sign-off before being ratified, since those two principles are constraints set by
the formateur's brief rather than internal project decisions.

**Versioning policy** (semantic versioning applied to this document):
- **MAJOR**: a principle is removed or redefined in a backward-incompatible way
  (e.g., dropping a non-negotiable, changing the imposed stack).
- **MINOR**: a new principle or section is added, or existing guidance is
  materially expanded.
- **PATCH**: wording clarifications, typo fixes, non-semantic refinements.

**Compliance review**: every `/speckit-plan` MUST include a Constitution Check
gate evaluated against the principles above before Phase 0 research and
re-checked after Phase 1 design; any violation MUST be justified in that plan's
Complexity Tracking table or the plan MUST be revised. `CLAUDE.md` remains the
day-to-day operational guidance file (commands, repo-specific conventions); this
constitution is the higher-authority source when the two disagree.

**Version**: 1.0.0 | **Ratified**: 2026-07-11 | **Last Amended**: 2026-07-11
