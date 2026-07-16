"""Garde-fous d'entrée et de sortie de l'agent Velmo.

Surface publique stable consommée par l'agent et la suite d'acceptance.
Contrôle en entrée ET en sortie : aucune catégorie interdite ne passe dans un
sens comme dans l'autre (docs/reco_expert.md, exigence n°2). Toute décision de
blocage est journalisée (docs/reco_expert.md, principe d'observabilité).
"""

from __future__ import annotations

import re
import unicodedata

from dataclasses import dataclass, field

# Catégories de contenus contrôlés.
CATEGORIES = (
    "hate",
    "violence",
    "sexual",
    "pii",
    "out_of_scope",
    "prompt_injection",
    "secret_leak",
)


def _normalize(texte: str) -> str:
    """Minuscules + suppression des accents : « clé » et « cle » deviennent identiques."""
    decompose = unicodedata.normalize("NFD", texte.lower())
    return "".join(c for c in decompose if unicodedata.category(c) != "Mn")


def _contient(texte_norm: str, cles: list[str]) -> bool:
    """Cherche chaque mot-clé ANCRÉ AU DÉBUT d'un mot.

    Le simple `cle in texte` cherchait n'importe où dans la chaîne et bloquait des
    clients légitimes : « bourse » dans « rem-bourse-ment », « race » dans « t-race-r »,
    « tuer » dans « effec-tuer ».

    On n'ancre QUE le début (`(?<!\\w)`), jamais la fin : « sous-humain » doit continuer
    à matcher « sous-humain·s » (pluriel) et « hais » à matcher « haissent ». Ancrer la
    fin aussi ferait passer la haine au pluriel — donc une fuite grave.
    """
    return any(re.search(rf"(?<!\w){re.escape(cle)}", texte_norm) for cle in cles)


@dataclass
class Decision:
    """Verdict d'un garde-fou sur un message."""

    allowed: bool
    action: str  # "allow" | "block"
    category: str | None = None
    reason: str = ""
    refusal: str | None = None


@dataclass
class GuardrailEngine:
    """Applique les garde-fous d'entrée et de sortie et journalise les décisions."""

    events: list[dict] = field(default_factory=list)

    # Mots-clés par catégorie (écrits sans accents ; `_normalize` aligne les messages).
    INPUT_KEYWORDS = {
        "prompt_injection": ["ignore tes instructions", "oublie tes consignes",
                             "developer mode", "prompt systeme"],
        "secret_leak": ["cle api", "mot de passe", "variables d'environnement",
                        "token", "secret"],
        "out_of_scope": ["combien vaut", "cote", "revente", "investir", "bourse",
                         "authentifier", "juridique"],
        "hate": ["hais", "race", "sous-etre", "sous-humain"],
        "violence": ["frapper", "tuer", "menace", "faire du mal"],
        "sexual": ["sexuel", "nudite"],
    }

    # Numéro de carte : 16 chiffres en 4 groupes de 4 (espace ou tiret optionnel entre).
    CARD_RE = re.compile(r"\b\d{4}[ -]?\d{4}[ -]?\d{4}[ -]?\d{4}\b")

    def _journalise(self, where: str, categorie: str, message: str) -> None:
        """Trace toute décision de blocage, entrée comme sortie."""
        self.events.append({"where": where, "category": categorie,
                            "action": "block", "message": message})

    def check_input(self, message: str) -> Decision:
        """Contrôle un message entrant (PII, modération, injection, périmètre)."""
        # 1) PII entrante : un client ne doit pas taper sa carte dans le chat.
        if self.CARD_RE.search(message):
            self._journalise("input", "pii", message)
            return Decision(
                allowed=False, action="block", category="pii",
                refusal="Ne partagez jamais vos coordonnées bancaires dans le chat.",
            )
        # 2) modération, injection, secrets, hors-périmètre
        low = _normalize(message)
        for categorie, cles in self.INPUT_KEYWORDS.items():
            if _contient(low, cles):
                self._journalise("input", categorie, message)
                return Decision(
                    allowed=False, action="block", category=categorie,
                    refusal="Désolé, je ne peux pas traiter cette demande.",
                )
        # 3) rien de suspect -> on laisse passer
        return Decision(allowed=True, action="allow")

    def check_output(self, text: str) -> Decision:
        """Contrôle une réponse sortante (PII, secrets, périmètre, modération)."""
        # 1) fuite de donnée personnelle : un numéro de carte
        if self.CARD_RE.search(text):
            self._journalise("output", "pii", text)
            return Decision(
                allowed=False, action="block", category="pii",
                refusal="Désolé, je ne peux pas transmettre cette information.",
            )
        # 2) mêmes catégories des deux côtés : on réutilise les mots-clés
        low = _normalize(text)
        for categorie, cles in self.INPUT_KEYWORDS.items():
            if _contient(low, cles):
                self._journalise("output", categorie, text)
                return Decision(
                    allowed=False, action="block", category=categorie,
                    refusal="Désolé, je ne peux pas transmettre cette information.",
                )
        # 3) rien de sensible -> on laisse passer
        return Decision(allowed=True, action="allow")
