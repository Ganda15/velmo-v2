# STUDY GUIDE — Chantier 3, in 6 sessions

> **Read this one first.** You have 9 documents and ~270 KB of material. This file is the
> **map**: where to start, in what order, and how to check you've understood.
>
> **Total time**: about 3 hours, in 6 sessions of ~30 minutes. Don't do it in one sitting.
>
> **Rule for every session**: open **VS Code** on the left, the document on the right. When I
> give you a file and a line, **go look at it**. Reading about code is not understanding code.

---

## Before anything: the one sentence

> **Chantiers 1 and 2 added behaviour. Chantier 3 proves we didn't break it.**

If you remember nothing else, remember that. Everything below is the detail of *how*.

---

## The state today (measured, 2026-07-17)

```
19 passed, 0 failed          the trainer's 3 tests are green
score 0.825                  memory 0.500 · guardrails 1.000 · quality 1.000
CI gate: ACTIVE              quality.yml can now refuse a delivery
```

**Not done yet**: pushing to GitHub to *see* the gate refuse a PR · 3 questions for the trainer.

---

# SESSION 1 — The shape of the thing (30 min)

**Goal**: be able to draw the pipeline from memory.

### Read
`COURS-chantier3-EN.md` — sections **1** and **2** only. Stop after the file table.

### Look at
The picture: `schema-chantier3-boucle-qualite.png`

### The pipeline, in words
```
3 data files  →  one loader  →  3 suites  →  one score  →  a report  →  the CI gate
```

### Self-check — answer out loud, without looking
1. Why does Chantier 3 exist at all?
2. What are the 3 suites, and what does each one measure?
3. What are the 4 design decisions the trainer validated?
4. What happens if the score is exactly 0.800?

> **If you can't answer #4**: it *passes*. Strict `<`. A threshold is a bar to clear, not a wall
> to exceed.

---

# SESSION 2 — The gate where data enters (30 min)

**Goal**: understand *fail-closed*, the idea the whole chantier rests on.

### Read
`COURS-chantier3-EN.md` — section **4** (T004).

### Open in VS Code
`src/velmo/mlops/cases.py` — 61 lines, read the whole file.
- **line 12** — `EVAL_DIR`, and why `parents[3]` and not `parents[2]`
- **line 19** — `_load_jsonl`, the only function with safety logic
- **lines 28-30** — why blank lines are skipped *inside* the loop

### The idea to hold on to
An empty guardrail file → 0 cases → the suite returns **100%** → the CI ships an agent with no
guardrails.

> **A wrong measurement is worse than no measurement, because you trust it.**

### Self-check
1. Why one loader instead of three?
2. Name the 4 reasons it raises `EvalDataError`.
3. Why does the error message carry the file **and** the line number?
4. What would break if we filtered blank lines *before* `enumerate`?

---

# SESSION 3 — The three suites, three isolations (40 min)

**Goal**: understand why the three suites don't look alike — and why that's correct.

### Read
`COURS-chantier3-EN.md` — sections **5, 6, 7** (T005, T006, T007).

### Open in VS Code — in this order
1. `src/velmo/mlops/suites/guardrail_suite.py` (62 lines) — the clearest one
2. `src/velmo/mlops/suites/quality_suite.py` (30 lines) — the shortest
3. `src/velmo/mlops/suites/memory_suite.py` (43 lines) — the one with the deviation

### The table to memorise
| Suite | Calls | Isolation | Why |
|---|---|---|---|
| guardrails | `check_input` directly | component | so a red names ONE culprit |
| memory | `read()` after replay | component | isolate memory from the LLM |
| quality | **`respond()`** | **integration** | "does it do its job" IS a whole-chain question |

> **The measuring tool adapts to what's being measured.** That's the answer if the trainer asks
> why they're inconsistent.

### Self-check
1. Why does the guardrail suite refuse to call `respond()`?
2. Why is the guardrail score a **multiplication** and not an average?
3. Which 5 categories trigger `serious_leak`, and why not `prompt_injection`?
4. Why does T005 read the memory **state** instead of the answer? *(this one is a deviation from
   what the trainer validated — you must be able to explain it)*

---

# SESSION 4 — From three scores to one decision (30 min)

**Goal**: be able to defend `scoring.py` line by line.

### Read
`COURS-chantier3-EN.md` — sections **8** and **9** (T008, T009/T010/T013).

### Open in VS Code
`src/velmo/mlops/scoring.py` (130 lines)
- **line 77** — `_snap`
- **line 81** — `aggregate`, the whole function
- **lines 90-99** — the LLM wrapper and the `finally` that restores it

Then `src/velmo/mlops/__init__.py` (64 lines) — read it entirely, it's the public contract.

### The four decisions
1. **×3 runs** — useless today (the suites are deterministic), essential the day a real LLM is
   plugged in. *The protection must be there before the problem.*
2. **Snap the sub-scores**, never the global. Snapping the global gives 0.82 instead of 0.825 —
   a different calculation from the validated one.
3. **The cap overrides.** One serious leak on one run out of three → global = 0.0. **Proven**:
   an agent with a weighted mean of 0.811 (which would have passed) scores 0.0.
4. **Two counters**: 186 agent calls (latency) vs 27 LLM calls (cost). *Confusing them meant
   paying for regex.*

### Self-check
1. Why keep the ×3 if the suites are deterministic?
2. What does the `finally` at line 99 protect?
3. Why is `Scores` `frozen=True`?
4. Why does `aggregate()` return a **dict** and not a `Scores`?

---

# SESSION 5 — Report, CLI, gate (30 min)

**Goal**: understand how a number becomes a refusal.

### Read
`COURS-chantier3-EN.md` — sections **11, 12, 13** (T012, T014, T015).

### Open in VS Code
1. `src/velmo/mlops/report.py` (47 lines) — look at **lines 14-17**, the comment explaining the
   missing accents
2. `src/velmo/mlops/score.py` (69 lines) — **line 56 then line 59**, in that order
3. `.github/workflows/quality.yml` — the last step

### Run it yourself
```bash
.\.venv\Scripts\python.exe -m velmo.mlops.score --min-score 0.8    # exit 0
.\.venv\Scripts\python.exe -m velmo.mlops.score --min-score 0.99   # exit 1
```
Then open `mlops/report.md` **after the second command**. It exists. That's the point.

### The idea to hold on to
> **The report must survive the failure it explains.** Written *before* the verdict — otherwise
> a block would prevent it from existing, and you'd have an `exit 1` with no document.

### Self-check
1. Why are the report labels written without accents?
2. Why does cost say `N/A` instead of `0.00`?
3. Why is `write_report` called before `enforce_threshold`?
4. What does `--live` change, and why isn't it the default?

---

# SESSION 6 — What the loop found, and what it teaches (30 min)

**Goal**: this is your oral material. The strongest part.

### Read
`COURS-chantier3-EN.md` — sections **14** (what we fixed in Chantier 1) and **15** (the 8
lessons).

### The story to be able to tell
The quality loop ran **once**, before it was even finished, and it pointed at **3 real bugs in
Chantier 1**. We fixed them under its control. Score went **0.767 → 0.825**.

And it found what the unit tests could never find — because `test_memory.py` calls
`mm.forget()` **directly**, so nobody ever noticed the **agent** was doing it wrong.

> **The quality loop tests the agent, not the bricks. It sees what unit tests cannot.**

### The thread through everything
**A green that lies is worse than a red.** Six measured occurrences in two days — including
three I produced myself and had to correct.

### Self-check
1. What 3 bugs did the loop find in Chantier 1?
2. Why did `test_memory.py` never catch them?
3. Give two examples of "a green that lies" from this project.
4. Why is 6/12 an *honest* score rather than a failure?

---

# WHEN YOU'RE READY — the decisions waiting for you

Don't read this until sessions 1-6 are done. These are **your** calls, and you need the
understanding first.

### Decision 1 — the 3 questions for the trainer
| # | question | why it matters |
|---|---|---|
| 1 | Do you validate evaluating the **memory state** rather than the phrased answer? | **It contradicts what he validated.** He must hear it from you. |
| 2 | Do you validate the **method** — the loop points, I fix, I re-measure? | This is what makes Chantier 3 worth something. |
| 3 | The **float trap**: 32 combos out of 75 at exactly 0.8 get wrongly blocked. | It's asleep today (margin 0.025). It wakes when memory improves. |

### Decision 2 — the push, and the red PR
The repo is **PUBLIC**. ~57 commits live on one disk only.

```
1. make it private       gh repo edit Ganda15/velmo-v2 --visibility private
2. push main             → Actions: GREEN
3. branch, break a guardrail on purpose
4. open a PR             → Actions: RED, "note globale 0.000 < seuil 0.800"
5. screenshot            → C13 demonstrated, not narrated
```

> **A green run proves it works. A RED run proves it's useful.** That's the one the jury wants.

### Decision 3 — the 8 technical debts
All documented in `COURS-chantier3-EN.md` section 16. **None blocks delivery.** The most urgent
is #1 (a non-object JSON line raises `AttributeError`, not `EvalDataError`) — it must be closed
*before* any `exit 2 INVALID` work.

---

## If you only have 20 minutes before seeing the trainer

Read, in this order:
1. **This file** — "the one sentence" + "the state today"
2. `COURS-chantier3-EN.md` **section 15** — the 8 lessons
3. `oral-blocage-T005-formateur.md` — the 30-second summary at the top

That's enough to hold a serious conversation.

---

## Commands

```bash
.\.venv\Scripts\python.exe -m pytest tests/ -q                   # 19 passed
.\.venv\Scripts\python.exe -m velmo.mlops.score --min-score 0.8  # exit 0, ~1 s
.\.venv\Scripts\python.exe -m velmo.mlops.score --live           # ~90 s, real stack
.\.venv\Scripts\python.exe -m velmo.ui.app                       # http://127.0.0.1:7860
docker compose up -d                                             # Postgres 5434 · Chroma 8011
```

⚠️ **Always `.\.venv\Scripts\python.exe`** — the system `python` gives `ModuleNotFoundError`.
