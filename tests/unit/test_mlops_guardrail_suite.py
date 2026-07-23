"""Tests unitaires — velmo.mlops.suites.guardrail_suite : calcul des taux."""

from __future__ import annotations

from velmo.guardrails import Decision
from velmo.mlops.suites import guardrail_suite as gs


class _FakeGuardrails:
    def check_input(self, message: str) -> Decision:
        blocked = message == "BLOCK"
        return Decision(allowed=not blocked, action="block" if blocked else "allow")

    def check_output(self, text: str) -> Decision:
        blocked = text == "BLOCK"
        return Decision(allowed=not blocked, action="block" if blocked else "allow")


class _FakeAgent:
    guardrails = _FakeGuardrails()


def test_run_guardrail_suite_counts_false_positive(monkeypatch):
    cases = [
        {"where": "input", "message": "BLOCK", "expected_action": "allow", "category": "n/a"},
        {"where": "input", "message": "ok", "expected_action": "allow", "category": "n/a"},
        {"where": "output", "message": "BLOCK", "expected_action": "block", "category": "pii"},
    ]
    monkeypatch.setattr(gs, "load_guardrail_cases", lambda: cases)

    result = gs.run_guardrail_suite(_FakeAgent())

    assert result.block_rate == 1.0
    assert result.false_positive_rate == 0.5  # 1 faux positif sur 2 cas "allow"
