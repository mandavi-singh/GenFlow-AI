import pytest
from fastapi.testclient import TestClient

import genflow.store as store_mod
from genflow import rag
from genflow.ui import server as srv


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(store_mod, "STORE_PATH", tmp_path / "chats.json")
    monkeypatch.setattr(srv, "_warmup_model", lambda: None)
    return TestClient(srv.app)


def test_index_serves_ui(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "GenFlow-AI" in resp.text


def test_auth_status_reports_no_password(client):
    resp = client.get("/api/auth/status")
    assert resp.status_code == 200
    assert resp.json() == {"required": False}


def test_chat_endpoint_persists_exchange(client, monkeypatch):
    async def fake_flow(question, history):
        return "stub reply"

    monkeypatch.setattr(srv, "run_chat_flow", fake_flow)

    resp = client.post("/api/chat", json={"message": "hello"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["reply"] == "stub reply"

    chats = client.get("/api/chats").json()
    assert len(chats) == 1
    assert chats[0]["messages_count"] == 2


def test_research_endpoint_returns_report(client, monkeypatch):
    async def fake_research(query):
        return "stub report"

    monkeypatch.setattr(srv, "run_research_flow", fake_research)

    resp = client.post("/api/research", json={"query": "quantum computing"})
    assert resp.status_code == 200
    assert resp.json()["report"] == "stub report"


def test_rag_ask_endpoint(client, monkeypatch):
    async def fake_answer(question):
        return "stub answer"

    monkeypatch.setattr(rag, "answer_from_docs", fake_answer)

    resp = client.post("/api/rag/ask", json={"question": "what is the budget?"})
    assert resp.status_code == 200
    assert resp.json()["answer"] == "stub answer"


def test_chat_returns_503_when_engine_unreachable(client, monkeypatch):
    async def failing_flow(question, history):
        raise ConnectionError("Connection refused")

    monkeypatch.setattr(srv, "run_chat_flow", failing_flow)

    resp = client.post("/api/chat", json={"message": "hello"})
    assert resp.status_code == 503
    assert "AI engine" in resp.json()["detail"]


def test_models_endpoint_reports_current(client):
    resp = client.get("/api/models")
    assert resp.status_code == 200
    assert "current" in resp.json()
