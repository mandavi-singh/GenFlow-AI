<div align="center">

<img src="docs/banner.svg" alt="GenFlow-AI banner" width="100%"/>

# GenFlow-AI

**Multi-agent GenAI research assistant — fully local, zero API keys.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?logo=langchain&logoColor=white)](https://langchain.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C)](https://langchain-ai.github.io/langgraph/)
[![Ollama](https://img.shields.io/badge/Ollama-121621?logo=ollama&logoColor=white)](https://ollama.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Chat · Research · Docs (RAG) · Voice — sab kuch tumhare PC par, koi data bahar nahi jata.

</div>

---

## Features

| Feature | Description |
|---|---|
| **Chat** | Conversational AI with memory + persistent history (JSON store) |
| **Research** | Multi-agent pipeline: researcher (ReAct + MCP tools) → writer → critic loop |
| **Docs (RAG)** | Upload PDF / PPTX / TXT / MD — ask questions answered from your documents |
| **Voice** | Local Whisper speech-to-text (mic) + browser text-to-speech |
| **Hindi / Hinglish** | Roman typing → Hinglish reply; Hindi speech → natural Hindi reply |
| **Chat sidebar** | ChatGPT-style: list, open, rename (double-click), delete, new chat |
| **Model switcher** | UI dropdown — switch Ollama models anytime (qwen3:1.7b / 4b-instruct) |
| **Resilient** | Auto-retry with exponential backoff on engine overload; friendly error messages |

## Architecture

```
Browser UI (sidebar, chat, tabs)
   │
FastAPI server  ──  store.py (data/chats.json — chat history)
   │
 ├─ Chat flow     → LangChain → Ollama (qwen3:4b-instruct)
 ├─ Research flow → LangGraph: researcher (MCP tools) → writer → critic
 ├─ Docs flow     → RAG: nomic-embed-text + InMemoryVectorStore
 └─ Voice         → faster-whisper (local STT)
   │
 Ollama (localhost:11434) — all models local
```

<details>
<summary><b>Project structure</b></summary>

```
GenFlow-AI/
├── src/genflow/
│   ├── agents/
│   │   ├── research_graph.py   # LangGraph multi-agent pipeline
│   │   ├── react_graph.py      # generic ReAct tool-calling graph
│   │   └── state.py            # ResearchState
│   ├── mcp_tools/
│   │   ├── server.py           # MCP server (FastMCP)
│   │   └── client.py           # langchain-mcp-adapters client
│   ├── flows/research_flow.py  # chat + research entrypoints
│   ├── ui/
│   │   ├── server.py           # FastAPI app (all endpoints)
│   │   └── static/index.html   # web UI
│   ├── rag.py                  # RAG: ingest, search, answer
│   ├── stt.py                  # Whisper speech-to-text
│   ├── store.py                # chat history (JSON)
│   ├── llm.py                  # Ollama client + retry logic
│   ├── config.py               # settings (.env)
│   └── cli.py                  # `genflow` command
├── data/
│   ├── docs/                   # uploaded documents (RAG) — gitignored
│   └── chats.json              # chat history — gitignored
└── tests/
```

</details>

## Setup

### 1. Requirements

- Python 3.10+
- [Ollama](https://ollama.com/download) installed and running

### 2. Install

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\pip install -e ".[dev]"
ollama pull qwen3:4b-instruct
ollama pull nomic-embed-text   # RAG embeddings
```

### 3. Configure (optional)

`.env` — defaults shown:

```env
GENFLOW_MODEL=qwen3:4b-instruct
GENFLOW_BASE_URL=http://localhost:11434
GENFLOW_TEMPERATURE=0.2
```

Optional: set `GENFLOW_PASSWORD` to lock chat history behind a password.

## Run

```powershell
.\.venv\Scripts\Activate.ps1
genflow serve                  # UI: http://127.0.0.1:8000
genflow chat "hello"           # CLI quick chat
genflow research "topic"       # CLI multi-agent research
```

LAN access (other devices on your network):

```powershell
genflow serve 0.0.0.0 8000
```

## Use

1. **Chat tab** — type your question (mic button to speak it, speaker toggle for spoken answers)
2. **Research tab** — deep multi-agent reports (30-90s: researcher → writer → critic loop)
3. **Docs tab** — upload PDF/PPTX/TXT, then ask anything about them; filename mentions are routed to that exact file
4. **Sidebar** — history: click to open, double-click to rename, x to delete, + for new chat
5. **Model dropdown** (top-left) — switch models anytime

<details>
<summary><b>Screenshots</b></summary>

> Chat, Research aur Docs tabs ke screenshots yahan add karne hain:
> `docs/screenshot-chat.png`, `docs/screenshot-research.png`, `docs/screenshot-docs.png`
>
> App chala kar (Ctrl+PrtScn ya Win+Shift+S) le lo, `docs/` folder mein save karo, phir yahan embed:
>
> ```markdown
> | Chat | Docs (RAG) |
> |---|---|
> | ![Chat](docs/screenshot-chat.png) | ![Docs](docs/screenshot-docs.png) |
> ```

</details>

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/chat` | Chat reply (with history) |
| `POST` | `/api/research` | Multi-agent research report |
| `POST` | `/api/rag/upload` | Upload document for RAG |
| `POST` | `/api/rag/ask` | Ask question over indexed docs |
| `POST` | `/api/rag/ingest` | Re-index documents folder |
| `POST` | `/api/stt` | Speech-to-text (audio file) |
| `GET/POST` | `/api/models`, `/api/model` | List / switch Ollama models |
| `GET/POST/...` | `/api/chats` | Chat history CRUD |

## Test / Lint

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
.\.venv\Scripts\python.exe -m ruff check src tests
```

## Tech Stack

**Backend:** Python · FastAPI · LangChain · LangGraph · langchain-mcp-adapters · MCP (FastMCP) · langchain-ollama
**AI:** Ollama (qwen3) · nomic-embed-text (embeddings) · faster-whisper (STT)
**Frontend:** Vanilla JS + CSS (single-file, no build step)
**Storage:** JSON (chats) · InMemoryVectorStore + JSON dump (RAG index)

## Notes

- All inference local: Ollama (qwen3) + Whisper — no API keys, unlimited usage, full privacy
- Uploaded documents and chat history stay in `data/` — never pushed to git (see `.gitignore`)
- RAM: 8GB+ recommended (4b model ~3GB); close heavy browser tabs for best speed
- Voice input needs mic permission (browser); STT runs locally via faster-whisper

## License

MIT — see [LICENSE](LICENSE)

## Author

**Mandavi Singh** — [GitHub](https://github.com/mandavi-singh)

<div align="center">
Made with Python, LangGraph and fully-local AI
</div>
