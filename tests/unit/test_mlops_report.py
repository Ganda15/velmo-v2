"""Tests unitaires — velmo.mlops.report : rendu du coût quand le tarif est configuré."""

from __future__ import annotations

from velmo.mlops import Scores, report


def test_render_shows_cost_when_tariff_configured(monkeypatch):
    monkeypatch.setenv("EVAL_COST_PER_CALL", "0.002")
    scores = Scores(
        memory=1.0, guardrails=1.0, quality=1.0, global_=1.0,
        block_rate=0.0, false_positive_rate=0.0, latency_ms=1.0, cost=1.2345,
    )
    text = report.render(scores)
    assert "1.2345" in text
