"""Chargeur unique et fail-closed pour les 3 suites d'evaluation (memoire, garde-fous, qualite).

Une seule fonction porte la securite (_load_jsonl) pour qu'une regle appliquee a un seul
endroit reste une regle, pas une intention repetee trois fois.
"""

from __future__ import annotations

import json
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parents[3] / "eval"


class EvalDataError(Exception):
    """Donnee d'evaluation invalide ou manquante (fail-closed, jamais rattrapee)."""


def _load_jsonl(path: Path) -> list[dict]:
    if not path.is_file():
        raise EvalDataError(f"{path} — fichier introuvable")

    texte = path.read_text(encoding="utf-8")

    cases: list[dict] = []
    seen_ids: dict[str, int] = {}

    for line_number, line in enumerate(texte.splitlines(), start=1):
        if not line.strip():
            continue

        try:
            case = json.loads(line)
        except json.JSONDecodeError as exc:
            raise EvalDataError(f"{path}:{line_number} — JSON invalide : {exc}") from exc

        case_id = case.get("id")
        if case_id in seen_ids:
            raise EvalDataError(
                f"{path}:{line_number} — id duplique : {case_id!r} "
                f"(deja vu ligne {seen_ids[case_id]})"
            )
        seen_ids[case_id] = line_number
        cases.append(case)

    if not cases:
        raise EvalDataError(f"{path} — fichier vide (aucun cas d'evaluation)")

    return cases


def load_memory_cases() -> list[dict]:
    return _load_jsonl(EVAL_DIR / "memory_cases.jsonl")


def load_guardrail_cases() -> list[dict]:
    return _load_jsonl(EVAL_DIR / "guardrail_cases.jsonl")


def load_quality_cases() -> list[dict]:
    return _load_jsonl(EVAL_DIR / "quality_cases.jsonl")
