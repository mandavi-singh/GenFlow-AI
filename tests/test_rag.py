import hashlib

import pytest

from genflow import rag


class _FakeEmbeddings:
    """Deterministic offline stand-in for Ollama embeddings."""

    def _vec(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        return [b / 255 for b in digest[:8]]

    def embed_documents(self, texts):
        return [self._vec(t) for t in texts]

    def embed_query(self, text):
        return self._vec(text)


@pytest.fixture(autouse=True)
def _isolate_rag(tmp_path, monkeypatch):
    monkeypatch.setattr(rag, "DOCS_DIR", tmp_path / "docs")
    monkeypatch.setattr(rag, "INDEX_PATH", tmp_path / "index.json")
    monkeypatch.setattr(rag, "_get_embeddings", lambda: _FakeEmbeddings())
    rag._store = None


def test_search_without_index_returns_empty():
    assert rag.search("anything") == []


def test_ingest_empty_directory(tmp_path):
    assert rag.ingest_directory(tmp_path / "empty") == {"indexed_files": 0, "chunks": 0}


def test_ingest_then_search_finds_document(tmp_path):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "report.txt").write_text(
        "The JalSanrakshan scheme has a budget of Rs 4.2 crore.", encoding="utf-8"
    )

    result = rag.ingest_directory()
    assert result["indexed_files"] == 1
    assert result["chunks"] >= 1

    hits = rag.search("budget", k=4)
    assert hits
    assert all(h.metadata["source"] == "report.txt" for h in hits)


def test_re_ingesting_does_not_duplicate_chunks(tmp_path):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "report.txt").write_text("Budget is Rs 4.2 crore.", encoding="utf-8")

    first = rag.ingest_directory()
    assert first["chunks"] == 1
    assert rag.ingest_directory()["chunks"] == 1


def test_status_lists_files(tmp_path):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "report.txt").write_text("hello", encoding="utf-8")

    status = rag.status()
    assert status["files"] == ["report.txt"]
    assert status["indexed"] is False


def test_type_routing_by_word_token():
    assert rag._wanted_extensions("tell me about this pd") == [".pdf"]
    assert rag._wanted_extensions("show me the pdf") == [".pdf"]
    assert rag._wanted_extensions("what is in the pptx") == [".pptx"]
    assert rag._wanted_extensions("summarize the slides") == [".pptx"]


def test_type_routing_ignores_false_positives():
    assert rag._wanted_extensions("please update the notes") == []
    assert rag._wanted_extensions("what is the capital of france") == []
