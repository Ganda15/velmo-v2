"""Chat interactif avec le VRAI modèle Kimi-K2.6 (Azure AI Foundry).

Le brief l'impose : docs/reco_expert.md ligne 9 — « LLM via API : Azure AI
Inference, modele Kimi-K2.6. Aucun modele local. »

Prerequis (une seule fois) :
    uv sync --extra llm                 # installe langchain-azure-ai
    Copy-Item .env.example .env         # puis remplir les 3 valeurs AZURE_*
    git check-ignore -v .env            # DOIT afficher une ligne

Lancer :
    .\\.venv\\Scripts\\python.exe docs2\\chat_azure.py

Base SQLite en RAM et FAQ locale : le vrai LLM ne demande pas Docker.
Les garde-fous sont les memes que hors-ligne — c'est tout le point.
"""

import sys
from pathlib import Path

from dotenv import load_dotenv

# .env DOIT etre charge AVANT get_llm() : get_llm lit os.getenv a l'execution.
load_dotenv()

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tests"))

from conftest import seeded_session  # noqa: E402
from velmo.agent import Agent  # noqa: E402
from velmo.guardrails import GuardrailEngine  # noqa: E402
from velmo.kb_store import LocalKB  # noqa: E402
from velmo.llm import get_llm  # noqa: E402
from velmo.memory import MemoryManager  # noqa: E402

USER = "C-marc-dubois"
AIDE = "Commandes : journal · aide · quitter"


def affiche_journal(agent) -> None:
    if not agent.guardrails.events:
        print("        (aucun blocage pour l'instant)\n")
        return
    print(f"        {'OU':<7} | {'CATEGORIE':<17} | MESSAGE")
    print(f"        {'-' * 7} | {'-' * 17} | {'-' * 45}")
    for e in agent.guardrails.events:
        print(f"        {e['where']:<7} | {e['category']:<17} | {e['message'][:45]}")
    print()


def main() -> None:
    llm = get_llm()
    nom = type(llm).__name__

    if nom == "EchoLLM":
        print("STOP — AZURE_AI_INFERENCE_ENDPOINT n'est pas defini.")
        print("Le fichier .env est absent, mal nomme, ou la ligne endpoint est vide.")
        print("Sans lui, get_llm() (llm.py:45) renvoie le repli hors-ligne.")
        sys.exit(1)

    agent = Agent(
        llm=llm,                        # AzureLLM -> Kimi-K2.6 sur Azure AI Foundry
        memory=MemoryManager(),
        guardrails=GuardrailEngine(),   # les MEMES garde-fous qu'en hors-ligne
        session=seeded_session(),       # SQLite en RAM : pas besoin de Docker
        kb=LocalKB(),
    )

    print(f"Velmo 2.0 — support client (connecte : {USER})")
    print(f"LLM : {nom} — Kimi-K2.6 via Azure AI Foundry")
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
