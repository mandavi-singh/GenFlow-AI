import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

STORE_PATH = Path(__file__).resolve().parents[2] / "data" / "chats.json"
_lock = threading.Lock()


def _load() -> dict:
    if not STORE_PATH.exists():
        return {"chats": {}}
    return json.loads(STORE_PATH.read_text(encoding="utf-8"))


def _save(data: dict) -> None:
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STORE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def list_chats() -> list[dict]:
    with _lock:
        data = _load()
    out = []
    for cid, chat in data["chats"].items():
        out.append(
            {
                "id": cid,
                "title": chat["title"],
                "created_at": chat["created_at"],
                "updated_at": chat["updated_at"],
                "messages_count": len(chat["messages"]),
            }
        )
    out.sort(key=lambda c: c["updated_at"], reverse=True)
    return out


def get_chat(chat_id: str) -> dict | None:
    with _lock:
        data = _load()
    return data["chats"].get(chat_id)


def create_chat(title: str = "New chat") -> dict:
    chat_id = uuid.uuid4().hex[:12]
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with _lock:
        data = _load()
        data["chats"][chat_id] = {
            "title": title,
            "created_at": now,
            "updated_at": now,
            "messages": [],
        }
        _save(data)
    return {"id": chat_id, **get_chat(chat_id)}


def add_messages(chat_id: str, user_msg: str, assistant_msg: str) -> dict:
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with _lock:
        data = _load()
        chat = data["chats"].get(chat_id)
        if chat is None:
            chat = {
                "title": user_msg[:40],
                "created_at": now,
                "updated_at": now,
                "messages": [],
            }
            data["chats"][chat_id] = chat
        if not chat["messages"]:
            chat["title"] = user_msg[:40]
        chat["messages"].append({"role": "user", "content": user_msg})
        chat["messages"].append({"role": "assistant", "content": assistant_msg})
        chat["updated_at"] = now
        _save(data)
    return get_chat(chat_id)


def delete_chat(chat_id: str) -> None:
    with _lock:
        data = _load()
        data["chats"].pop(chat_id, None)
        _save(data)


def clear_all_chats() -> int:
    with _lock:
        data = _load()
        count = len(data["chats"])
        data["chats"] = {}
        _save(data)
    return count


def rename_chat(chat_id: str, title: str) -> dict | None:
    with _lock:
        data = _load()
        chat = data["chats"].get(chat_id)
        if chat is None:
            return None
        chat["title"] = title[:60]
        chat["updated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        _save(data)
    return get_chat(chat_id)
