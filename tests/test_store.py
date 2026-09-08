from genflow import store as store_mod
from genflow.store import (
    add_messages,
    create_chat,
    delete_chat,
    get_chat,
    list_chats,
    rename_chat,
)


def test_chat_lifecycle(tmp_path, monkeypatch):
    monkeypatch.setattr(store_mod, "STORE_PATH", tmp_path / "chats.json")

    chat = create_chat("test")
    cid = chat["id"]
    assert chat["title"] == "test"
    assert chat["messages"] == []

    add_messages(cid, "hello", "hi there")
    stored = get_chat(cid)
    assert len(stored["messages"]) == 2
    assert stored["messages"][0]["content"] == "hello"
    assert stored["title"] == "hello"

    renamed = rename_chat(cid, "renamed")
    assert renamed["title"] == "renamed"

    assert [c["id"] for c in list_chats()] == [cid]

    delete_chat(cid)
    assert get_chat(cid) is None
    assert list_chats() == []


def test_rename_missing_chat_returns_none(tmp_path, monkeypatch):
    monkeypatch.setattr(store_mod, "STORE_PATH", tmp_path / "chats.json")
    assert rename_chat("nope", "x") is None
