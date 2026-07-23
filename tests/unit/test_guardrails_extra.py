"""Tests unitaires complémentaires — velmo.guardrails : PII en entrée."""

from __future__ import annotations

from velmo.guardrails import GuardrailEngine


def test_input_card_number_is_blocked():
    engine = GuardrailEngine()
    decision = engine.check_input("Voici ma carte : 4111 1111 1111 1111, utilisez-la.")
    assert decision.action == "block"
    assert decision.category == "pii"
    assert len(engine.events) == 1
