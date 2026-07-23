"""Tests unitaires — velmo.tools.returns : ouverture de retour/échange."""

from __future__ import annotations

from velmo.db import Return, ReturnStatus
from velmo.tools.returns import create_return


def test_create_return_not_found_or_forbidden(db_session):
    result = create_return(db_session, "O-2024-0107", "C-marc-dubois", "Erreur")
    assert result == {"error": "not_found_or_forbidden", "order_id": "O-2024-0107"}


def test_create_return_refused_when_not_delivered(db_session):
    result = create_return(db_session, "O-2024-0101", "C-marc-dubois", "Ne convient pas")
    assert result == {"action": "refused", "reason": "not_returnable", "status": "prepared"}


def test_create_return_opened_when_delivered(db_session):
    result = create_return(db_session, "O-2024-0105", "C-marc-dubois", "Erreur de taille")
    assert result["action"] == "return_opened"
    assert result["order_id"] == "O-2024-0105"

    stored = db_session.get(Return, result["return_id"])
    assert stored is not None
    assert stored.status == ReturnStatus.requested
    assert stored.reason == "Erreur de taille"
