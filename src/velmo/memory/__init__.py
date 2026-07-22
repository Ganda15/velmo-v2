"""Mémoire de l'agent Velmo : contexte court terme et mémoire long terme.

Surface publique stable consommée par l'agent et la suite d'acceptance.
L'implémentation interne (court terme, long terme, orchestration) est à construire.
"""

from __future__ import annotations

import re

from dataclasses import dataclass, field

from sqlalchemy import select

from .store import MemoryFact, Session

Turn = tuple[str, str]  # (role, content)

# Motif « Ma commande prioritaire est X » / « Mes clubs préférés sont X ».
# Généralisation de la règle au pluriel (mes/sont) — révélée par la suite
# d'évaluation du Chantier 3 : « Mes clubs préférés sont l'OM » ne mémorisait
# RIEN. On complète la règle existante, on n'ajoute pas un cas particulier.
FACT_PATTERN = re.compile(
    r"\b(?:ma|mon|mes)\s+(.+?)\s+(?:est|sont)\s+(.+?)[.!?]?$",
    re.IGNORECASE,
)


@dataclass
class MemoryContext:
    """Contexte mémoire restitué pour une requête utilisateur."""

    history: list[Turn] = field(default_factory=list)
    facts: dict[str, str] = field(default_factory=dict)
    episodic: list[str] = field(default_factory=list)

    def render(self) -> str:
        """Sérialise le contexte en texte (injectable dans un prompt)."""
        parts: list[str] = []
        for role, content in self.history:
            parts.append(f"{role}: {content}")
        for key, value in self.facts.items():
            parts.append(f"fact:{key}={value}")
        parts.extend(self.episodic)
        return "\n".join(parts)


class MemoryManager:
    """Orchestre la mémoire court terme et long terme, isolée par utilisateur."""

    def __init__(self, *, token_budget: int = 2000) -> None:
        self.token_budget = token_budget

    def read(self, user_id: str, message: str) -> MemoryContext:
        """Reconstitue le contexte mémoire pertinent pour `message`."""
        with Session() as session:
            rows = session.scalars(
                select(MemoryFact).where(
                    MemoryFact.user_id == user_id,
                    MemoryFact.deleted.is_(False),
                )
            ).all()
            facts = {row.key: row.value for row in rows}
        return MemoryContext(facts=facts)

    def write(self, user_id: str, user_message: str, assistant_message: str) -> None:
        """Met à jour la mémoire à partir d'un échange."""
        match = FACT_PATTERN.search(user_message)
        if match is not None:
            key = match.group(1).strip().lower()
            value = match.group(2).strip()
            self.remember_fact(user_id, key, value)

    def remember_fact(self, user_id: str, key: str, value: str) -> None:
        """Persiste un fait durable sur l'utilisateur."""
        with Session() as session:
            existing = session.scalars(
                select(MemoryFact).where(
                    MemoryFact.user_id == user_id,
                    MemoryFact.key == key,
                    MemoryFact.deleted.is_(False),
                )
            ).first()
            if existing is not None:
                existing.value = value
            else:
                session.add(MemoryFact(user_id=user_id, key=key, value=value))
            session.commit()

    def forget(self, user_id: str, target: str) -> int:
        """Supprime les souvenirs correspondant à `target`. Renvoie le nombre supprimé."""
        # Correspondance MOT À MOT, pas sous-chaîne stricte : l'agent envoie
        # « adresse livraison » (articles filtrés) mais la clé stockée peut être
        # simplement « adresse » — la sous-chaîne échouait toujours. Un souvenir
        # matche si AU MOINS UN mot demandé apparaît dans sa clé ou sa valeur :
        # le client nomme souvent la chose plus précisément que ce qui est
        # stocké. Droit à l'oubli (R5, RGPD) : dans le doute, SUR-supprimer est
        # le sens sûr — rater une suppression est la faute, pas l'inverse.
        needle_words = target.strip().lower().split()
        if not needle_words:
            return 0
        with Session() as session:
            rows = session.scalars(
                select(MemoryFact).where(
                    MemoryFact.user_id == user_id,
                    MemoryFact.deleted.is_(False),
                )
            ).all()
            hits = [
                row for row in rows
                if any(w in row.key or w in row.value.lower() for w in needle_words)
            ]
            for row in hits:
                row.deleted = True
            session.commit()
            return len(hits)

    def inspect(self, user_id: str) -> dict:
        """Renvoie l'état mémoire d'un utilisateur — R6, traçabilité.

        Les faits actifs avec leur valeur, et les CLÉS de ceux qui ont été
        oubliés — pas leurs valeurs. C'est ici que l'effacement *logique*
        (`deleted`) paie : on prouve qu'une suppression a eu lieu sans
        ressusciter le contenu supprimé. Un `inspect()` qui rendrait la valeur
        oubliée annulerait le droit à l'oubli (R5) qu'il est censé tracer.

        Seule lecture du module qui regarde les lignes `deleted` — d'où
        l'absence de filtre ici, et le tri fait en Python juste après. Le
        filtre `user_id` reste, lui, non négociable (R3).
        """
        with Session() as session:
            rows = session.scalars(
                select(MemoryFact).where(MemoryFact.user_id == user_id)
            ).all()
            return {
                "facts": {row.key: row.value for row in rows if not row.deleted},
                "forgotten": sorted(row.key for row in rows if row.deleted),
                # Couche épisodique déclarée dans le modèle de données, pas
                # branchée. Vide et assumée vide — on n'invente pas.
                "episodic": [],
            }
