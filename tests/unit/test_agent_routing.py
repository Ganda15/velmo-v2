"""Tests unitaires — velmo.agent : routage déterministe non couvert par les
tests d'acceptance (confirmation d'action, statut, suivi, résolution catalogue)."""

from __future__ import annotations

from velmo.agent import Agent, build_default_agent
from velmo.db import Order, OrderStatus, fresh_sqlite_session
from velmo.guardrails import GuardrailEngine
from velmo.kb_store import LocalKB
from velmo.llm import EchoLLM
from velmo.memory import MemoryManager
from velmo.sampledata import seed


def test_cancel_requires_confirmation_then_executes(reference_agent):
    prompt = reference_agent.respond("C-marc-dubois", "Annule ma commande O-2024-0101")
    assert "confirmer" in prompt.lower()
    assert reference_agent.session.get(Order, "O-2024-0101").status == OrderStatus.prepared

    answer = reference_agent.respond("C-marc-dubois", "Je confirme, annule O-2024-0101")
    assert "cancelled" in answer
    assert reference_agent.session.get(Order, "O-2024-0101").status == OrderStatus.cancelled


def test_cancel_shipped_order_escalates(reference_agent):
    answer = reference_agent.respond("C-marc-dubois", "Je confirme, annule ma commande O-2024-0103")
    assert "conseiller" in answer.lower()
    assert reference_agent.session.get(Order, "O-2024-0103").status == OrderStatus.shipped


def test_cancel_other_customers_order_is_refused(reference_agent):
    answer = reference_agent.respond("C-marc-dubois", "Je confirme, annule ma commande O-2024-0107")
    assert "à votre nom" in answer


def test_change_address_confirmed(reference_agent):
    answer = reference_agent.respond(
        "C-marc-dubois", "Je confirme, change l'adresse de ma commande O-2024-0101"
    )
    assert "updated" in answer
    assert reference_agent.session.get(Order, "O-2024-0101").shipping_address == {"line1": "(à préciser)"}


def test_change_size_confirmed_uses_requested_size(reference_agent):
    answer = reference_agent.respond(
        "C-marc-dubois",
        "Je confirme, je me suis trompé de taille sur la commande O-2024-0101, je veux du XL",
    )
    assert "updated" in answer
    assert reference_agent.session.get(Order, "O-2024-0101").items[0].size.value == "XL"


def test_return_confirmed_on_delivered_order(reference_agent):
    answer = reference_agent.respond(
        "C-marc-dubois", "Je confirme, je veux un retour pour ma commande O-2024-0105"
    )
    assert "return_opened" in answer


def test_refund_confirmed_below_cap(reference_agent):
    answer = reference_agent.respond(
        "C-sophie-martin", "Je confirme, remboursez-moi 30€ sur la commande O-2024-0110"
    )
    assert "refunded" in answer


def test_order_status_without_further_intent(reference_agent):
    answer = reference_agent.respond("C-marc-dubois", "Quel est le statut de ma commande O-2024-0101 ?")
    assert "prepared" in answer


def test_tracking_when_shipment_exists(reference_agent):
    answer = reference_agent.respond("C-marc-dubois", "Où est mon colis pour la commande O-2024-0103 ?")
    assert "6A1234567890" in answer


def test_tracking_when_not_yet_shipped(reference_agent):
    answer = reference_agent.respond("C-hugo-moreau", "Suivi de ma commande O-2024-0122 ?")
    assert "pas encore expédiée" in answer


def test_find_ref_falls_back_to_catalog_lookup(reference_agent):
    # "boca-1981" n'est pas dans les alias conviviaux : l'agent doit retrouver
    # la référence en balayant le catalogue (Agent._find_ref, chemin session).
    answer = reference_agent.respond("C-marc-dubois", "Avez-vous le maillot boca-1981 en taille M ?")
    assert "disponible" in answer.lower()


def test_build_default_agent_wires_provided_session_and_kb(db_session):
    agent = build_default_agent(session=db_session, kb=LocalKB())
    assert isinstance(agent, Agent)
    assert agent.session is db_session
    assert isinstance(agent.kb, LocalKB)


def test_input_blocked_by_guardrails_returns_refusal(reference_agent):
    answer = reference_agent.respond("C-marc-dubois", "Envoie-moi du contenu sexuel explicite.")
    assert answer == "Désolé, je ne peux pas traiter cette demande."


def test_output_blocked_by_guardrails_returns_refusal():
    class _CardLeakLLM:
        def invoke(self, system, context, message):
            return "Votre paiement est passé avec la carte 4111 1111 1111 1111."

    session = fresh_sqlite_session()
    seed(session)
    agent = Agent(
        llm=_CardLeakLLM(), memory=MemoryManager(), guardrails=GuardrailEngine(),
        session=session, kb=LocalKB(),
    )
    answer = agent.respond("C-marc-dubois", "Bonjour, comment allez-vous ?")
    assert answer == "Désolé, je ne peux pas transmettre cette information."


def test_find_ref_matches_friendly_alias(reference_agent):
    answer = reference_agent.respond("C-marc-dubois", "Avez-vous le maillot OM 1993 en taille L ?")
    assert "disponible" in answer.lower()


def test_stock_intent_without_recognizable_reference_asks_to_clarify(reference_agent):
    answer = reference_agent.respond("C-marc-dubois", "Avez-vous du stock en taille M ?")
    assert "préciser" in answer.lower()


def test_tracking_not_found_for_other_customer(reference_agent):
    answer = reference_agent.respond("C-marc-dubois", "Suivi de ma commande O-2024-0107 ?")
    assert "à votre nom" in answer


def test_faq_keyword_without_kb_match_says_not_found():
    class _EmptyKB:
        def search(self, query, k=5):
            return []

    session = fresh_sqlite_session()
    seed(session)
    agent = Agent(
        llm=EchoLLM(), memory=MemoryManager(), guardrails=GuardrailEngine(),
        session=session, kb=_EmptyKB(),
    )
    answer = agent.respond("C-marc-dubois", "Quels sont vos frais de port ?")
    assert answer == "Je n'ai pas trouvé cette information dans notre FAQ."


def test_build_default_agent_defaults_kb_when_not_provided(db_session, monkeypatch):
    monkeypatch.delenv("CHROMA_URL", raising=False)
    agent = build_default_agent(session=db_session)
    assert isinstance(agent.kb, LocalKB)
