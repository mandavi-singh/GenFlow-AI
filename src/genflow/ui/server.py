import secrets
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from genflow import rag
from genflow.config import settings
from genflow.flows.research_flow import (
    run_chat_flow,
    run_research_flow,
    to_langchain_history,
)
from genflow.store import (
    add_messages,
    clear_all_chats,
    create_chat,
    delete_chat,
    get_chat,
    list_chats,
    rename_chat,
)

app = FastAPI(title="GenFlow-AI")
STATIC = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC), name="static")

SESSION_TOKEN = secrets.token_hex(16)


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if (
        settings.password
        and request.url.path.startswith("/api/")
        and request.url.path not in ("/api/auth/status", "/api/auth/login")
    ):
        auth = request.headers.get("Authorization", "")
        if auth != f"Bearer {SESSION_TOKEN}":
            return JSONResponse({"detail": "unauthorized"}, status_code=401)
    return await call_next(request)


class LoginRequest(BaseModel):
    password: str


class ChatRequest(BaseModel):
    message: str
    chat_id: str | None = None
    history: list[dict] = []


class ResearchRequest(BaseModel):
    query: str
    chat_id: str | None = None


class RagQuestion(BaseModel):
    question: str


class RenameRequest(BaseModel):
    title: str


class ModelRequest(BaseModel):
    model: str


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/auth/status")
def auth_status():
    return {"required": bool(settings.password)}


@app.post("/api/auth/login")
def login(req: LoginRequest):
    if not settings.password:
        return {"token": SESSION_TOKEN}
    if req.password != settings.password:
        raise HTTPException(401, "wrong password")
    return {"token": SESSION_TOKEN}


@app.get("/api/chats")
def api_list_chats():
    return list_chats()


@app.post("/api/chats")
def api_create_chat():
    return create_chat()


@app.get("/api/chats/{chat_id}")
def api_get_chat(chat_id: str):
    chat = get_chat(chat_id)
    if chat is None:
        raise HTTPException(404, "chat not found")
    return {"id": chat_id, **chat}


@app.delete("/api/chats")
def api_clear_chats():
    count = clear_all_chats()
    return {"cleared": count}


@app.delete("/api/chats/{chat_id}")
def api_delete_chat(chat_id: str):
    delete_chat(chat_id)
    return {"deleted": chat_id}


@app.patch("/api/chats/{chat_id}")
def api_rename_chat(chat_id: str, req: RenameRequest):
    chat = rename_chat(chat_id, req.title)
    if chat is None:
        raise HTTPException(404, "chat not found")
    return {"id": chat_id, **chat}


def _friendly_error(exc: Exception) -> str:
    msg = str(exc)
    if "admission rejected" in msg.lower() or "overloaded" in msg.lower():
        return (
            "The AI engine is currently busy with a large request. "
            "Please wait a few seconds and try again."
        )
    if "connection" in msg.lower() and ("refused" in msg.lower() or "reset" in msg.lower()):
        return (
            "Could not reach the AI engine (Ollama). "
            "Make sure it is running, then try again."
        )
    return "Something went wrong while generating the answer. Please try again."


@app.post("/api/chat")
async def chat(req: ChatRequest):
    chat_id = req.chat_id
    if not chat_id or get_chat(chat_id) is None:
        chat_id = create_chat(req.message[:40])["id"]
    history = to_langchain_history(req.history)
    try:
        reply = await run_chat_flow(req.message, history)
    except Exception as exc:
        raise HTTPException(503, _friendly_error(exc))
    add_messages(chat_id, req.message, reply)
    return {"reply": reply, "chat_id": chat_id}


@app.post("/api/research")
async def research(req: ResearchRequest):
    try:
        report = await run_research_flow(req.query)
    except Exception as exc:
        raise HTTPException(503, _friendly_error(exc))
    chat_id = req.chat_id
    if not chat_id or get_chat(chat_id) is None:
        chat_id = create_chat("Research: " + req.query[:30])["id"]
    add_messages(chat_id, req.query, report)
    return {"report": report, "chat_id": chat_id}


@app.get("/api/rag/status")
def rag_status():
    return rag.status()


@app.post("/api/rag/ingest")
def rag_ingest():
    return rag.ingest_directory()


@app.post("/api/rag/upload")
async def rag_upload(file: UploadFile):
    rag.DOCS_DIR.mkdir(parents=True, exist_ok=True)
    dest = rag.DOCS_DIR / Path(file.filename).name
    dest.write_bytes(await file.read())
    result = rag.ingest_directory()
    return {"saved": str(dest), **result}


@app.post("/api/rag/ask")
async def rag_ask(req: RagQuestion):
    try:
        answer = await rag.answer_from_docs(req.question)
    except Exception as exc:
        raise HTTPException(503, _friendly_error(exc))
    return {"answer": answer}


@app.post("/api/stt")
async def stt_transcribe(file: UploadFile):
    from genflow import stt

    audio = await file.read()
    result = stt.transcribe(audio)
    return result


@app.get("/api/models")
def api_models():
    import json as _json
    import urllib.request
    from urllib.error import URLError

    import genflow.llm as llm_mod

    models = []
    try:
        with urllib.request.urlopen(f"{settings.base_url}/api/tags", timeout=5) as r:
            data = _json.loads(r.read())
            models = [m["name"] for m in data.get("models", [])]
    except (URLError, OSError, ValueError):
        pass
    return {"current": llm_mod._model_override or settings.model, "available": models}


@app.post("/api/model")
async def api_set_model(req: ModelRequest):
    import genflow.llm as llm_mod

    llm_mod._model_override = req.model
    return {"model": req.model}
