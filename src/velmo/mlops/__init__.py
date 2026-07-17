"""Évaluation et MLOps de l'agent Velmo : suites, note globale, seuil, rapport.

Surface publique stable consommée par la suite d'acceptance et la CI.
L'exécution des suites, le calcul de la note et la production du rapport sont à construire.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from velmo.mlops.scoring import aggregate
from velmo.mlops.versioning import _config_snapshot, version_id


class Evaluable(Protocol):
    """Agent évaluable : expose mémoire, garde-fous et une réponse."""

    def respond(self, user_id: str, message: str) -> str: ...


@dataclass(frozen=True)
class Scores:
    """Notes d'une exécution d'évaluation."""

    memory: float
    guardrails: float
    quality: float
    global_: float
    block_rate: float
    false_positive_rate: float
    latency_ms: float
    cost: float


class DeliveryBlocked(Exception):
    """Levée quand la note globale passe sous le seuil de livraison."""


def run_eval(agent: Evaluable) -> Scores:
    """Exécute les trois suites (mémoire, garde-fous, qualité) et calcule les notes."""
    return Scores(**aggregate(agent))


def enforce_threshold(scores: Scores, min_score: float) -> None:
    """Bloque la livraison (lève `DeliveryBlocked`) si la note globale est trop basse."""
    if scores.global_ < min_score:
        raise DeliveryBlocked(
            f"note globale {scores.global_:.3f} < seuil {min_score:.3f} — livraison bloquee"
        )


def write_report(scores: Scores, path: Path) -> None:
    """Écrit le rapport de suivi (note mémoire, blocage, faux positifs, latence, coût)."""
    raise NotImplementedError("write_report")


def current_version() -> str:
    """Renvoie la version courante de l'agent évaluée."""
    return version_id(_config_snapshot())
