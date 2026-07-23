"""Tests unitaires — utilitaires partagés des outils (velmo.tools._common, velmo.tools.kb)."""

from __future__ import annotations

from velmo.db import Order
from velmo.tools._common import new_id, order_to_dict, owned_order
from velmo.tools.kb import search_kb


def test_owned_order_returns_order_for_matching_customer(db_session):
    order = owned_order(db_session, "O-2024-0101", "C-marc-dubois")
    assert isinstance(order, Order)
    assert order.id == "O-2024-0101"


def test_owned_order_returns_none_for_other_customer(db_session):
    assert owned_order(db_session, "O-2024-0101", "C-sophie-martin") is None


def test_owned_order_returns_none_for_unknown_order(db_session):
    assert owned_order(db_session, "O-9999-9999", "C-marc-dubois") is None


def test_order_to_dict_shape(db_session):
    order = db_session.get(Order, "O-2024-0101")
    result = order_to_dict(order)
    assert result == {
        "order_id": "O-2024-0101",
        "status": "prepared",
        "total": 250.0,
        "shipping_address": {"line1": "12 rue du Stade", "city": "Lyon", "zip": "69003", "country": "France"},
        "items": [{"item_id": "oi-0101", "variant_id": "v-france-1998-L", "size": "L"}],
    }


def test_new_id_is_prefixed_and_unique():
    a, b = new_id("rt"), new_id("rt")
    assert a.startswith("rt-") and b.startswith("rt-")
    assert a != b


def test_search_kb_reports_not_found_when_no_hits():
    class EmptyKB:
        def search(self, query: str, k: int = 5) -> list[dict]:
            return []

    result = search_kb(EmptyKB(), "question sans rapport")
    assert result == {"found": False, "query": "question sans rapport", "results": []}
