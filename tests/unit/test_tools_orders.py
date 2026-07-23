"""Tests unitaires — velmo.tools.orders : lecture, suivi, adresse, annulation."""

from __future__ import annotations

from velmo.db import Escalation, Order, OrderStatus
from velmo.tools._common import select
from velmo.tools.orders import (
    cancel_order,
    get_order,
    track_shipment,
    update_order_item,
    update_shipping_address,
)


def test_get_order_success(db_session):
    result = get_order(db_session, "O-2024-0101", "C-marc-dubois")
    assert result["order_id"] == "O-2024-0101"
    assert result["status"] == "prepared"


def test_get_order_not_found_or_forbidden(db_session):
    result = get_order(db_session, "O-2024-0101", "C-sophie-martin")
    assert result == {"error": "not_found_or_forbidden", "order_id": "O-2024-0101"}


def test_track_shipment_with_shipment(db_session):
    result = track_shipment(db_session, "O-2024-0103", "C-marc-dubois")
    assert result["carrier"] == "Colissimo"
    assert result["tracking_number"] == "6A1234567890"
    assert result["actual_delivery"] is None


def test_track_shipment_without_shipment_record(db_session):
    result = track_shipment(db_session, "O-2024-0122", "C-hugo-moreau")
    assert result == {"order_id": "O-2024-0122", "status": "prepared", "shipment": None}


def test_track_shipment_not_found_or_forbidden(db_session):
    result = track_shipment(db_session, "O-2024-0107", "C-marc-dubois")
    assert result == {"error": "not_found_or_forbidden", "order_id": "O-2024-0107"}


def test_update_shipping_address_when_modifiable(db_session):
    new_address = {"line1": "9 rue Neuve", "city": "Lyon", "zip": "69001", "country": "France"}
    result = update_shipping_address(db_session, "O-2024-0101", "C-marc-dubois", new_address)
    assert result == {"action": "updated", "order_id": "O-2024-0101", "address": new_address}
    assert db_session.get(Order, "O-2024-0101").shipping_address == new_address


def test_update_shipping_address_escalates_when_shipped(db_session):
    before = len(db_session.scalars(select(Escalation)).all())
    result = update_shipping_address(db_session, "O-2024-0103", "C-marc-dubois", {"line1": "x"})
    assert result["action"] == "escalate"
    assert result["status"] == "shipped"
    after = len(db_session.scalars(select(Escalation)).all())
    assert after == before + 1


def test_update_shipping_address_not_found_or_forbidden(db_session):
    result = update_shipping_address(db_session, "O-2024-0107", "C-marc-dubois", {"line1": "x"})
    assert result == {"error": "not_found_or_forbidden", "order_id": "O-2024-0107"}


def test_cancel_order_when_modifiable(db_session):
    result = cancel_order(db_session, "O-2024-0122", "C-hugo-moreau")
    assert result == {"action": "cancelled", "order_id": "O-2024-0122"}
    assert db_session.get(Order, "O-2024-0122").status == OrderStatus.cancelled


def test_cancel_order_escalates_when_shipped(db_session):
    result = cancel_order(db_session, "O-2024-0124", "C-ines-garcia")
    assert result["action"] == "escalate"
    assert db_session.get(Order, "O-2024-0124").status == OrderStatus.shipped  # inchangé


def test_cancel_order_not_found_or_forbidden(db_session):
    result = cancel_order(db_session, "O-2024-0110", "C-marc-dubois")
    assert result == {"error": "not_found_or_forbidden", "order_id": "O-2024-0110"}


def test_update_order_item_not_found_or_forbidden(db_session):
    result = update_order_item(db_session, "O-2024-0107", "C-marc-dubois", "M")
    assert result == {"error": "not_found_or_forbidden", "order_id": "O-2024-0107"}
