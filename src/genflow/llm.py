import asyncio
import re

from langchain_ollama import ChatOllama

from genflow.config import settings

_model_override = None

_OVERLOAD_PATTERNS = (
    re.compile(r"admission rejected", re.IGNORECASE),
    re.compile(r"overloaded|server busy|too many requests", re.IGNORECASE),
    re.compile(r"connection refused|connection reset|timed?\s*out", re.IGNORECASE),
)
_RETRY_ATTEMPTS = 4
_RETRY_BASE_DELAY = 1.5


def _is_transient(exc: BaseException) -> bool:
    if isinstance(exc, (ConnectionError, TimeoutError, OSError)):
        return True
    return any(p.search(str(exc)) for p in _OVERLOAD_PATTERNS)


async def ainvoke_with_retry(llm, messages):
    last_exc: BaseException | None = None
    for attempt in range(_RETRY_ATTEMPTS):
        try:
            return await llm.ainvoke(messages)
        except Exception as exc:
            last_exc = exc
            if not _is_transient(exc) or attempt == _RETRY_ATTEMPTS - 1:
                raise
            await asyncio.sleep(_RETRY_BASE_DELAY * (2**attempt))
    raise last_exc


def get_llm(**kwargs) -> ChatOllama:
    merged = {
        "model": _model_override or settings.model,
        "temperature": settings.temperature,
        "base_url": settings.base_url,
        "reasoning": False,
        "num_ctx": 2048,
        "num_predict": 400,
        "repeat_penalty": 1.15,
    }
    merged.update(kwargs)
    return ChatOllama(**merged)
