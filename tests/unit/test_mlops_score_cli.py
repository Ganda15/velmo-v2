"""Tests unitaires — velmo.mlops.score : CLI d'évaluation qualité (contracts/cli.md)."""

from __future__ import annotations

from velmo.mlops import Scores
from velmo.mlops import score as score_cli

_GOOD = Scores(
    memory=1.0, guardrails=1.0, quality=1.0, global_=0.95,
    block_rate=0.0, false_positive_rate=0.0, latency_ms=5.0, cost=0.0,
)
_BAD = Scores(
    memory=0.2, guardrails=0.2, quality=0.2, global_=0.2,
    block_rate=0.5, false_positive_rate=0.5, latency_ms=5.0, cost=0.0,
)


def test_score_cli_writes_report_and_exits_zero_above_threshold(tmp_path, monkeypatch):
    monkeypatch.setattr(score_cli, "run_eval", lambda agent: _GOOD)
    report_path = tmp_path / "report.md"

    exit_code = score_cli.main(["--min-score", "0.8", "--report", str(report_path)])

    assert exit_code == 0
    assert report_path.exists()
    assert "0.950" in report_path.read_text(encoding="utf-8")


def test_score_cli_blocks_delivery_below_threshold(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(score_cli, "run_eval", lambda agent: _BAD)
    report_path = tmp_path / "report.md"

    exit_code = score_cli.main(["--min-score", "0.8", "--report", str(report_path)])

    assert exit_code == 1
    assert "bloquee" in capsys.readouterr().err
    assert report_path.exists()  # le rapport est écrit même en cas de blocage
