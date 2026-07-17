"""Rendu Markdown du rapport d'evaluation (C20 — signaux de suivi qualite)."""

from __future__ import annotations

import os
from datetime import UTC, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from velmo.mlops import Scores


def render(scores: "Scores") -> str:
    # Libelles deliberement SANS ACCENTS ("memoire", "cout", jamais "mémoire" /
    # "coût") : le test d'acceptance cherche ces chaines ASCII apres .lower(),
    # et .lower() ne retire PAS les accents ("mémoire".lower() reste
    # "mémoire"). Ne pas "corriger" l'orthographe ici — ça casserait le test.

    # Import differe : current_version() vit dans velmo.mlops (__init__.py),
    # qui importera ce module pour write_report (T013). Un import en tete de
    # fichier creerait un cycle __init__ -> report -> __init__.
    from velmo.mlops import current_version

    if os.getenv("EVAL_COST_PER_CALL"):
        cout = f"{scores.cost:.4f}"
    else:
        # Zero invente = mensonge : ca ressemble a "gratuit" alors que c'est
        # "tarif non configure". On distingue "mesure a zero" de "inconnu".
        cout = "N/A (aucun tarif configure — EVAL_COST_PER_CALL non defini)"

    horodatage = datetime.now(UTC).isoformat()

    return (
        "# Rapport d'evaluation Velmo\n\n"
        f"Version : {current_version()}\n"
        f"Horodatage : {horodatage}\n\n"
        "## Notes\n\n"
        f"- Score memoire : {scores.memory:.3f}\n"
        f"- Score garde-fous : {scores.guardrails:.3f}\n"
        f"- Score qualite : {scores.quality:.3f}\n"
        f"- Note globale : {scores.global_:.3f}\n\n"
        "## Signaux\n\n"
        f"- Taux de blocage : {scores.block_rate:.3f}\n"
        f"- Taux de faux positifs : {scores.false_positive_rate:.3f}\n"
        f"- Latence : {scores.latency_ms:.2f} ms\n"
        f"- Cout : {cout}\n"
    )
