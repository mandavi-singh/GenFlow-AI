---
title: GenFlow-AI
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
license: mit
short_description: Multi-agent GenAI research assistant - fully local LLM stack
---

# GenFlow-AI — Live Demo

Multi-agent GenAI research assistant running **fully inside this Space** — no external APIs, no API keys. Ollama + qwen3:1.7b + FastAPI + LangGraph + RAG, all in a single Docker container.

> Note: a small model (1.7b) runs on the free CPU tier, so replies are slower and simpler. A local setup with qwen3:4b-instruct is faster and more accurate.

## What's inside

| Tab | What it does |
|---|---|
| **Chat** | Conversational AI with history |
| **Research** | Multi-agent pipeline: researcher → writer → critic |
| **Docs** | RAG — upload your own documents and ask questions (PDF/PPTX/TXT) |

Full source code: [github.com/mandavi-singh/GenFlow-AI](https://github.com/mandavi-singh/GenFlow-AI)
