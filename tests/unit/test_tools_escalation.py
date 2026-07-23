"""Tests unitaires — velmo.tools.escalation : passage de main à un humain."""

from __future__ import annotations

from velmo.db import Escalation
from velmo.tools.escalation import escalate_to_human


def test_escalate_to_human_with_order(db_session):
    result = escalate_to_human(db_session, "C-marc-dubois", "Litige montant", order_id="O-2024-0101")
    assert result["action"] == "escalated"
    assert result["reason"] == "Litige montant"

    stored = db_session.get(Escalation, result["escalation_id"])
    assert stored.customer_id == "C-marc-dubois"
    assert stored.order_id == "O-2024-0101"


def test_escalate_to_human_without_order(db_session):
    result = escalate_to_human(db_session, "C-marc-dubois", "Demande volume revendeur")
    stored = db_session.get(Escalation, result["escalation_id"])
    assert stored.order_id is None
