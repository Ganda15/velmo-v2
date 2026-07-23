"""Tests unitaires complémentaires — velmo.memory : rendu épisodique, forget vide, MEMORY_DB_URL."""

from __future__ import annotations

from velmo.memory import MemoryContext, MemoryManager
from velmo.memory import store as memory_store


def test_render_includes_episodic_layer():
    context = MemoryContext(history=[("user", "salut")], episodic=["fait épisodique X"])
    rendered = context.render()
    assert "fait épisodique X" in rendered


def test_forget_with_blank_target_returns_zero():
    mm = MemoryManager()
    assert mm.forget("some-user", "   ") == 0


def test_build_engine_uses_memory_db_url_when_set(monkeypatch):
    monkeypatch.setenv("MEMORY_DB_URL", "sqlite:///:memory:")
    engine = memory_store._build_engine()
    assert str(engine.url) == "sqlite:///:memory:"
