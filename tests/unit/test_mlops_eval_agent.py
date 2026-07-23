"""Tests unitaires — velmo.mlops.eval_agent : assemblage de l'agent d'évaluation."""

from __future__ import annotations

from velmo.agent import Agent
from velmo.db import Product
from velmo.kb_store import LocalKB
from velmo.llm import EchoLLM
from velmo.mlops.eval_agent import build_eval_agent


def test_build_eval_agent_is_seeded_offline_agent(monkeypatch):
    monkeypatch.delenv("AZURE_AI_INFERENCE_ENDPOINT", raising=False)

    agent = build_eval_agent()

    assert isinstance(agent, Agent)
    assert isinstance(agent.llm, EchoLLM)
    assert isinstance(agent.kb, LocalKB)
    assert agent.session.get(Product, "mu-1999-treble") is not None  # seed() appliqué
