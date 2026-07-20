"""Suite d'evaluation memoire : verifie l'ETAT memoire apres rejeu de la
conversation, jamais la phrase produite par le LLM.

Raison : l'agent d'evaluation utilise EchoLLM (conftest le code en dur), qui
repete la question au lieu d'y repondre. Verifier la phrase donnerait 0/12 et
bloquerait l'agent SAIN. On mesure la memoire, pas le talent du modele a
formuler — meme raison qui fait que la suite garde-fous appelle le portique en
direct. Ecart assume par rapport a la conception initiale.
Voir docs/conception/03-modele-donnees-memoire.md."""

from __future__ import annotations

from dataclasses import dataclass

from velmo.mlops.cases import load_memory_cases


@dataclass
class MemorySuiteResult:
    score: float
    passed: int
    total: int


def run_memory_suite(agent) -> MemorySuiteResult:
    cases = load_memory_cases()

    passed = 0
    for case in cases:
        for turn in case["turns"]:
            if turn["role"] == "user":
                agent.respond(case["user_id"], turn["content"])

        ev = case["evaluation"]
        facts = agent.memory.read(case["user_id"], ev["question"]).facts
        blob = " | ".join(f"{k}={v}" for k, v in facts.items()).lower()

        if ev["type"] == "forget":
            case_passed = ev["forbidden_substring"].lower() not in blob
        else:
            case_passed = ev["expected_substring"].lower() in blob

        if case_passed:
            passed += 1

    total = len(cases)
    score = passed / total if total else 0.0

    return MemorySuiteResult(score=score, passed=passed, total=total)
