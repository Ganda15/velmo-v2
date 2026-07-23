"""Tests unitaires — velmo.mlops.cases : chargeur fail-closed des cas d'évaluation."""

from __future__ import annotations

import pytest

from velmo.mlops.cases import EvalDataError, _load_jsonl


def test_missing_file_raises(tmp_path):
    with pytest.raises(EvalDataError, match="introuvable"):
        _load_jsonl(tmp_path / "does-not-exist.jsonl")


def test_invalid_json_raises(tmp_path):
    path = tmp_path / "cases.jsonl"
    path.write_text('{"id": "a"}\nceci n\'est pas du json\n', encoding="utf-8")
    with pytest.raises(EvalDataError, match="JSON invalide"):
        _load_jsonl(path)


def test_duplicate_id_raises(tmp_path):
    path = tmp_path / "cases.jsonl"
    path.write_text('{"id": "a"}\n{"id": "a"}\n', encoding="utf-8")
    with pytest.raises(EvalDataError, match="id duplique"):
        _load_jsonl(path)


def test_empty_file_raises(tmp_path):
    path = tmp_path / "cases.jsonl"
    path.write_text("\n   \n", encoding="utf-8")
    with pytest.raises(EvalDataError, match="fichier vide"):
        _load_jsonl(path)


def test_valid_file_is_parsed_and_blank_lines_skipped(tmp_path):
    path = tmp_path / "cases.jsonl"
    path.write_text('{"id": "a"}\n\n{"id": "b"}\n', encoding="utf-8")
    assert _load_jsonl(path) == [{"id": "a"}, {"id": "b"}]
