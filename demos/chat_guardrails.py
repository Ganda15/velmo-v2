"""Chat interactif avec l'agent Velmo — garde-fous actifs, entièrement hors-ligne.

Lancer depuis C:\\Users\\kanda\\velmo-v2 :

    .\\.venv\\Scripts\\python.exe docs2\\chat_guardrails.py

Ce script ne modifie rien. Il importe la fabrique d'agent des tests et appelle
`agent.respond()` — jamais `check_input` ni `check_output` directement. C'est
précisément ce qui prouve que les garde-fous sont BRANCHÉS dans `agent.py`
(lignes 71 et 80), et pas seulement fonctionnels en isolation.

Base SQLite en RAM : rien n'est écrit sur le disque, la mémoire meurt à la sortie.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tests"))

from conftest import build_reference_agent  # noqa: E402

USER = "C-marc-dubois"  # client réel du jeu de données (sampledata.py)

AIDE = "Commandes : journal · aide · quitter"


def affiche_journal(agent) -> None:
    """Le journal est celui de l'agent lui-même, pas une copie."""
    if not agent.guardrails.events:
        print("        (aucun blocage pour l'instant)\n")
        return
    print(f"        {'OU':<7} | {'CATEGORIE':<17} | MESSAGE")
    print(f"        {'-' * 7} | {'-' * 17} | {'-' * 45}")
    for e in agent.guardrails.events:
        print(f"        {e['where']:<7} | {e['category']:<17} | {e['message'][:45]}")
    print()


def main() -> None:
    agent = build_reference_agent()
    print(f"Velmo 2.0 — support client (connecte : {USER})")
    print(f"{AIDE}\n")

    while True:
        try:
            message = input("Vous  : ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nA bientot !")
            break

        if not message:
            continue
        if message.lower() in ("quitter", "exit", "quit"):
            print("A bientot !")
            break
        if message.lower() == "aide":
            print(AIDE)
            continue
        if message.lower() == "journal":
            affiche_journal(agent)
            continue

        print(f"Velmo : {agent.respond(USER, message)}\n")


if __name__ == "__main__":
    main()
