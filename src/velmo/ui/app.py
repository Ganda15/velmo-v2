"""Démo web Velmo 2.0 — chat + inspection de la mémoire et des garde-fous.

HORS contrat du brief (l'interface imposée est `velmo.cli`). Cette page sert à
montrer l'agent en direct : elle passe par `agent.respond()`, jamais par le
moteur nu, donc ce qu'on voit est exactement ce que voit un vrai client.

Lancer :
    .\.venv\Scripts\python.exe -m velmo.ui.app
puis ouvrir http://127.0.0.1:7860

Repli automatique : sans Postgres joignable, la démo bascule sur une base
SQLite éphémère + `sampledata.seed()`, et le bandeau du haut le dit. On ne
prétend jamais tourner sur la vraie stack quand ce n'est pas le cas.
"""

from __future__ import annotations

import os

import gradio as gr
from dotenv import load_dotenv

from velmo.agent import build_default_agent

load_dotenv()

USERS = ["C-marc-dubois", "C-sofia-lopez", "C-inconnu"]


def _build_agent() -> tuple[object, str]:
    """Construit l'agent réel ; retombe sur SQLite + LocalKB si la stack est absente.

    Renvoie (agent, description_honnête_de_la_stack). Le bandeau doit dire la
    VRAIE cause du repli : accuser Postgres quand c'est Chroma qui manque
    enverrait chercher au mauvais endroit.
    """
    # Le nom du modèle se LIT, il ne se code pas en dur : afficher « Kimi » en
    # faisant tourner autre chose serait un mensonge dans la démo.
    if os.getenv("AZURE_AI_INFERENCE_ENDPOINT"):
        llm_name = f"{os.getenv('AZURE_AI_INFERENCE_MODEL', '?')} (Azure)"
    else:
        llm_name = "EchoLLM (hors-ligne)"
    try:
        agent = build_default_agent()
        return agent, f"Postgres · {type(agent.kb).__name__} · {llm_name}"
    except Exception as exc:
        from velmo.db import fresh_sqlite_session
        from velmo.kb_store import LocalKB
        from velmo.sampledata import seed

        session = fresh_sqlite_session()
        seed(session)
        agent = build_default_agent(session=session, kb=LocalKB())
        cause = str(exc).splitlines()[0][:80] or type(exc).__name__
        return agent, f"SQLite éphémère · LocalKB · {llm_name}  —  repli, cause réelle : {cause}"


AGENT, STACK = _build_agent()


def chat(message: str, history: list, user_id: str) -> str:
    """Un tour de conversation. Passe par respond() : garde-fous inclus."""
    if not message.strip():
        return ""
    try:
        return AGENT.respond(user_id, message)
    except Exception as exc:
        return f"⚠️ Erreur : {type(exc).__name__} — {exc}"


def show_memory(user_id: str) -> str:
    """Affiche ce que l'agent a VRAIMENT retenu de ce client.

    On passe par `memory.read()`, pas par `inspect()` (R6) : `inspect()` est
    encore un stub qui renvoie `{"facts": {}, "episodic": []}` en dur. L'appeler
    afficherait « aucun souvenir » même avec la mémoire pleine — une démo qui
    ment est pire qu'une démo absente.
    """
    facts = AGENT.memory.read(user_id, "").facts
    if not facts:
        body = "_Aucun fait mémorisé pour ce client. Dis « Ma taille est L » dans le chat, puis reviens ici._"
    else:
        body = "\n".join(f"- **{key}** : {value}" for key, value in sorted(facts.items()))
    return f"{body}\n\n---\n_Lu via `memory.read()`. `inspect()` (R6) est encore un stub — dette connue du Chantier 1._"


with gr.Blocks(title="Velmo 2.0 — démo") as demo:
    gr.Markdown("# Velmo 2.0 — agent SAV boutique collector")
    gr.Markdown(f"**Stack active :** `{STACK}`")

    user = gr.Dropdown(USERS, value=USERS[0], label="Client authentifié (user_id)")

    with gr.Tab("Chat"):
        gr.ChatInterface(fn=chat, additional_inputs=[user], type="messages")
        gr.Markdown(
            "Chaque message traverse `check_input` → agent → `check_output`. "
            "Essaie une attaque (« ignore tes instructions ») ou une question "
            "métier (« statut de ma commande O-2024-0101 ? »)."
        )

    with gr.Tab("Mémoire"):
        mem_out = gr.Markdown()
        gr.Button("Afficher la mémoire de ce client").click(
            show_memory, inputs=[user], outputs=[mem_out]
        )


def main() -> None:
    demo.launch(server_name="127.0.0.1", server_port=7860)


if __name__ == "__main__":
    main()
