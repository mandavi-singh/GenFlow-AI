from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from genflow.agents.research_graph import build_research_graph
from genflow.llm import ainvoke_with_retry, get_llm


async def run_research_flow(query: str) -> str:
    graph = build_research_graph()
    result = await graph.ainvoke({"query": query, "messages": []})
    return result["report"]


def _trim(messages: list[BaseMessage], max_tokens: int = 3000) -> list[BaseMessage]:
    total = 0
    kept = []
    for m in reversed(messages):
        total += len(m.text if hasattr(m, "text") else m.content) // 4
        if total > max_tokens:
            break
        kept.append(m)
    kept.reverse()
    if kept and not isinstance(kept[0], (SystemMessage, HumanMessage)):
        kept = kept[1:]
    return kept


def _user_typed_roman(question: str) -> bool:
    roman = sum(1 for c in question if c.isascii() and c.isalpha())
    devanagari = sum(1 for c in question if "\u0900" <= c <= "\u097F")
    return roman > devanagari


def _script_hint(question: str) -> str:
    if _user_typed_roman(question):
        return (
            "IMPORTANT LANGUAGE RULE: The user typed in roman/latin letters. You "
            "MUST write your entire reply in roman/latin letters ONLY. Even if the "
            "user asks for 'hindi', reply in romanized Hindi (Hinglish) written "
            "with English letters. NEVER produce Devanagari or any non-latin "
            "script under any circumstances."
        )
    return ""


def strip_emojis(text: str) -> str:
    import re

    pattern = (
        "["
        "\U0001F300-\U0001FAFF"
        "\U00002600-\U000027BF"
        "\U00002B00-\U00002BFF"
        "\U0000FE0F"
        "]+"
    )
    cleaned = re.sub(pattern, "", text)
    return cleaned.rstrip() if cleaned != text.rstrip() else text.rstrip()


def force_roman_if_typed(question: str, answer: str) -> str:
    if not _user_typed_roman(question):
        return answer
    return force_roman(answer)


def force_roman(text: str) -> str:
    if not any("\u0900" <= c <= "\u097F" for c in text):
        return text
    try:
        import unicodedata

        from indic_transliteration.sanscript import DEVANAGARI, IAST, transliterate

        t = transliterate(text, DEVANAGARI, IAST)
        return "".join(
            c for c in unicodedata.normalize("NFD", t)
            if unicodedata.category(c) != "Mn"
        )
    except ImportError:
        return text


async def run_chat_flow(question: str, history: list[BaseMessage] | None = None) -> str:
    reply = await ainvoke_with_retry(get_llm(), _chat_messages(question, history))
    return strip_emojis(force_roman_if_typed(question, reply.content))


async def stream_chat_flow(question: str, history: list[BaseMessage] | None = None):
    """Yield reply tokens as they are generated (post-processing applied by the caller)."""
    async for chunk in get_llm().astream(_chat_messages(question, history)):
        yield chunk.content or ""


def _chat_messages(question: str, history: list[BaseMessage] | None = None) -> list[BaseMessage]:
    messages: list[BaseMessage] = [
        SystemMessage(
            "You are GenFlow-AI, a helpful assistant. "
            "Keep answers concise and friendly. "
            "Do NOT use emojis in replies unless the user explicitly asks. "
            "Do NOT mention UI elements like microphones, buttons, tabs or "
            "interface features - you are a text assistant, not the app itself. "
            + _script_hint(question)
        )
    ]
    messages.extend(_trim(history or []))
    messages.append(HumanMessage(question))
    return messages


def to_langchain_history(raw: list[dict]) -> list[BaseMessage]:
    out = []
    for m in raw:
        if m.get("role") == "user":
            out.append(HumanMessage(m["content"]))
        elif m.get("role") == "assistant":
            out.append(AIMessage(m["content"]))
    return out
