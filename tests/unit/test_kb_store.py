"""Tests unitaires — velmo.kb_store : backend local (TF-IDF léger) et backend Chroma."""

from __future__ import annotations

import sys
import types

from velmo.kb_store import ChromaKB, LocalKB, get_kb


def test_local_kb_finds_relevant_document(tmp_path):
    (tmp_path / "port.md").write_text(
        "# Frais de port\n\nLes frais de port sont gratuits en France au-dessus de 100 euros.",
        encoding="utf-8",
    )
    (tmp_path / "garantie.md").write_text(
        "# Garanties\n\nLa garantie legale couvre deux ans.", encoding="utf-8"
    )

    kb = LocalKB(docs_dir=tmp_path)
    results = kb.search("frais de port")

    assert results
    assert results[0]["source"] == "port.md"


def test_local_kb_returns_empty_when_no_match(tmp_path):
    (tmp_path / "garantie.md").write_text("# Garanties\n\nDeux ans.", encoding="utf-8")
    kb = LocalKB(docs_dir=tmp_path)
    assert kb.search("mot totalement absent") == []


def test_local_kb_respects_k_limit_and_missing_dir(tmp_path):
    for name in ("doc_a", "doc_b", "doc_c"):
        (tmp_path / f"{name}.md").write_text(f"# {name}\n\nAvons-nous du reassort ?", encoding="utf-8")

    kb = LocalKB(docs_dir=tmp_path)
    assert len(kb.search("reassort ?", k=1)) == 1
    assert len(kb.search("reassort ?", k=5)) == 3

    empty_kb = LocalKB(docs_dir=tmp_path / "does-not-exist")
    assert empty_kb.docs == []
    assert empty_kb.search("reassort") == []


def test_chroma_kb_search_falls_back_to_default_source_when_metadata_missing():
    class FakeCollection:
        def query(self, query_texts, n_results):
            return {"documents": [["a", "b"]], "metadatas": [[None, {"source": "x.md"}]]}

    kb = ChromaKB(FakeCollection())
    results = kb.search("q", k=2)
    assert results == [{"source": "kb", "snippet": "a"}, {"source": "x.md", "snippet": "b"}]


def test_get_kb_returns_local_backend_without_chroma_url(monkeypatch):
    monkeypatch.delenv("CHROMA_URL", raising=False)
    assert isinstance(get_kb(), LocalKB)


def test_get_kb_returns_chroma_backend_when_configured(monkeypatch):
    calls: dict = {}

    class FakeCollection:
        def query(self, query_texts, n_results):
            return {"documents": [["extrait"]], "metadatas": [[{"source": "faq.md"}]]}

    class FakeHttpClient:
        def __init__(self, host, port):
            calls["host"], calls["port"] = host, port

        def get_or_create_collection(self, name, embedding_function):
            calls["collection_name"] = name
            return FakeCollection()

    class FakeEmbedder:
        def __init__(self, model_name):
            calls["model_name"] = model_name

    fake_chromadb = types.ModuleType("chromadb")
    fake_chromadb.HttpClient = FakeHttpClient
    fake_utils = types.ModuleType("chromadb.utils")
    fake_embedding_functions = types.ModuleType("chromadb.utils.embedding_functions")
    fake_embedding_functions.SentenceTransformerEmbeddingFunction = FakeEmbedder
    fake_utils.embedding_functions = fake_embedding_functions

    monkeypatch.setitem(sys.modules, "chromadb", fake_chromadb)
    monkeypatch.setitem(sys.modules, "chromadb.utils", fake_utils)
    monkeypatch.setitem(sys.modules, "chromadb.utils.embedding_functions", fake_embedding_functions)
    monkeypatch.setenv("CHROMA_URL", "http://chroma:8000")

    kb = get_kb()

    assert isinstance(kb, ChromaKB)
    assert calls["collection_name"] == "velmo_faq"
    assert kb.search("livraison") == [{"source": "faq.md", "snippet": "extrait"}]
