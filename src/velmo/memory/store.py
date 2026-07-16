"""Stockage relationnel des faits mémoire, isolé par user_id.

Source de vérité des faits durables (reco_expert : base relationnelle).
Par défaut : SQLite en mémoire PARTAGÉ (tests) ; Postgres si MEMORY_DB_URL est défini.
"""

from __future__ import annotations

import os

from sqlalchemy import Boolean, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy.pool import StaticPool


class MemoryBase(DeclarativeBase):
    pass


class MemoryFact(MemoryBase):
    __tablename__ = "memory_facts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, index=True)
    key: Mapped[str] = mapped_column(String)
    value: Mapped[str] = mapped_column(String)
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)


def _build_engine():
    """Engine partagé : Postgres si MEMORY_DB_URL, sinon SQLite mémoire partagé."""
    url = os.getenv("MEMORY_DB_URL")
    if url:
        return create_engine(url, future=True)
    # StaticPool : une seule base en mémoire vue par TOUTES les instances (R2).
    return create_engine(
        "sqlite://",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


_ENGINE = _build_engine()
MemoryBase.metadata.create_all(_ENGINE)
Session = sessionmaker(bind=_ENGINE, future=True)
