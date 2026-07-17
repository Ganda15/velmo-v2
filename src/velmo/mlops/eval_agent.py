"""Construit l'agent utilise par la CLI d'evaluation (score.py, T014).

Duplique volontairement le seedage de tests/conftest.py::seeded_session() —
src/ ne doit jamais importer depuis tests/ (research.md §6) : ca casserait
tout pip install / build de wheel qui n'embarque pas l'arbre de tests.
"""

from __future__ import annotations

from velmo.agent import Agent
from velmo.db import fresh_sqlite_session
from velmo.guardrails import GuardrailEngine
from velmo.kb_store import LocalKB
from velmo.llm import get_llm
from velmo.memory import MemoryManager
from velmo.sampledata import seed


def build_eval_agent() -> Agent:
    # fresh_sqlite_session() cree un engine SQLite en dur, sans jamais lire
    # DB_URL : meme si Postgres tourne, l'evaluation ne peut pas le toucher.
    session = fresh_sqlite_session()
    seed(session)
    return Agent(
        llm=get_llm(),
        memory=MemoryManager(),
        guardrails=GuardrailEngine(),
        session=session,
        kb=LocalKB(),
    )
