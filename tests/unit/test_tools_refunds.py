"""Tests unitaires — velmo.tools.refunds : branche non couverte par test_business.py."""

from __future__ import annotations

from velmo.tools.refunds import trigger_refund


def test_trigger_refund_not_found_or_forbidden(db_session):
    result = trigger_refund(db_session, "O-2024-0107", "C-marc-dubois", 10, "Geste")
    assert result == {"error": "not_found_or_forbidden", "order_id": "O-2024-0107"}
