"""Tests unitaires — velmo.tools.catalog : disponibilité / stock."""

from __future__ import annotations

from velmo.tools.catalog import check_stock


def test_check_stock_unknown_product(db_session):
    result = check_stock(db_session, "nope-1999", "M")
    assert result == {"error": "unknown_product", "product_ref": "nope-1999"}


def test_check_stock_unknown_size_variant(db_session):
    result = check_stock(db_session, "mu-1999-treble", "XXL")
    assert result == {"product_ref": "mu-1999-treble", "size": "XXL", "available": False, "stock": 0}


def test_check_stock_available(db_session):
    result = check_stock(db_session, "mu-1999-treble", "M")
    assert result["available"] is True
    assert result["stock"] == 1
    assert result["title"] == "Manchester United 1999 — Treble"


def test_check_stock_out_of_stock(db_session):
    result = check_stock(db_session, "om-1993", "M")
    assert result["available"] is False
    assert result["stock"] == 0
