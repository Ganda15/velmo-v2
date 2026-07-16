"""Démo interactive Velmo — chat + état de la mémoire à chaque tour.

Lancement (une seule commande) :
    uv run python docs2/demo_chat.py

Puis tape tes questions en français. Ctrl+C pour quitter.
Après chaque réponse, on affiche l'état de la mémoire (ce qui est retenu).
"""

from __future__ import annotations

import os

# Base de démo SQLite (le .env pointe vers Postgres, pas lancé en démo).
os.environ["DB_URL"] = "sqlite:///velmo-demo.db"
os.environ["CHROMA_URL"] = ""

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from velmo.db import Base
from velmo.sampledata import seed

load_dotenv()  # charge la clé Azure pour le vrai Kimi (facultatif)


def _prepare_db() -> None:
    """Recrée une base de démo fraîche et seedée."""
    if os.path.exists("velmo-demo.db"):
        os.remove("velmo-demo.db")
    engine = create_engine("sqlite:///velmo-demo.db", future=True)
    Base.metadata.create_all(engine)
    seed(sessionmaker(bind=engine, future=True)())


def _show_memory(agent, user: str) -> None:
    facts = agent.memory.read(user, "?").facts
    if facts:
        contenu = ", ".join(f"{k} = {v}" for k, v in facts.items())
        print(f"   🧠 Mémoire de {user} : {contenu}")
    else:
        print(f"   🧠 Mémoire de {user} : (vide)")


def main() -> None:
    _prepare_db()
    from velmo.agent import build_default_agent

    user = "C-marc-dubois"
    agent = build_default_agent()
    print(f"Velmo prêt (client {user}). Ctrl+C pour quitter.")
    _show_memory(agent, user)

    while True:
        try:
            message = input("\n👤 Vous : ").strip()
            if not message:
                continue
            answer = agent.respond(user, message)
            print(f"🤖 Velmo : {answer}")
            _show_memory(agent, user)
        except (KeyboardInterrupt, EOFError):
            print("\nÀ bientôt !")
            break


if __name__ == "__main__":
    main()
