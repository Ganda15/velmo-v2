# Quickstart: Quality Evaluation Loop

Validates the feature end-to-end once implemented. Run from the repo root with the venv
activated (or the AppLocker fallback interpreter per `CLAUDE.md`).

## Prerequisites

- `uv sync` (or the AppLocker fallback: `C:\Python314\python.exe -m pip install -e .`)
- No Postgres, no Chroma, no Docker required — everything in this feature runs against
  SQLite-in-memory and offline fallbacks (research.md §6).
- `eval/memory_cases.jsonl`, `eval/guardrail_cases.jsonl`, `eval/quality_cases.jsonl` already
  exist in the repo — nothing to seed.

## 1. Red → Green on the acceptance contract

```bash
python -m pytest tests/acceptance/test_mlops.py -v
```

Before implementation: all three tests fail (`run_eval` etc. raise `NotImplementedError`).
After implementation: all three pass — this is the TDD contract (constitution Principle II).

## 2. Exercise User Story 1 — versioned score, in isolation

```python
from conftest import build_reference_agent
from velmo.mlops import run_eval, current_version

scores = run_eval(build_reference_agent())
print(scores.global_, scores.memory, scores.guardrails, scores.quality)
print(current_version())
```

Expect: four floats in `[0.0, 1.0]`, a non-empty version id. Run twice — the version id must
be identical both times (nothing about the agent's config changed between calls).

## 3. Exercise User Story 2 — regression blocks delivery

```python
from conftest import build_degraded_agent, build_reference_agent
from velmo.mlops import DeliveryBlocked, enforce_threshold, run_eval

good = run_eval(build_reference_agent())
degraded = run_eval(build_degraded_agent())
assert degraded.global_ < good.global_

enforce_threshold(good, 0.8)          # must not raise
try:
    enforce_threshold(degraded, 0.8)  # must raise
    raise AssertionError("expected DeliveryBlocked")
except DeliveryBlocked:
    pass
```

## 4. Exercise User Story 3 — report signals

```python
from pathlib import Path
from conftest import build_reference_agent
from velmo.mlops import run_eval, write_report

scores = run_eval(build_reference_agent())
write_report(scores, Path("mlops/report.md"))
text = Path("mlops/report.md").read_text(encoding="utf-8").lower()
for signal in ["memoire", "blocage", "faux positif", "latence", "cout"]:
    assert signal in text
```

## 5. CI gate, locally

```bash
uv run python -m velmo.mlops.score --min-score 0.8
echo $?   # 0 = pass, 1 = DeliveryBlocked
cat mlops/report.md
```

## 6. Fail-closed check (edge case from spec.md)

Temporarily rename `eval/guardrail_cases.jsonl` and re-run step 5 — expect a non-zero exit
code and a traceback, **not** a passing report. Restore the file afterward.

## 7. Flip the CI gate on

Once steps 1–6 pass locally, uncomment the "Quality gate" step in
`.github/workflows/quality.yml` (contracts/cli.md) and push — CI now enforces the same gate.
