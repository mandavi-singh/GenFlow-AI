from langchain_core.tools import tool


@tool
def calculator(expression: str) -> str:
    """Safely evaluate a mathematical expression like '2**10 + 3.5'."""
    allowed = set("0123456789+-*/().% ")
    if not expression or any(c not in allowed for c in expression):
        return "error: unsupported characters in expression"
    try:
        return str(eval(expression, {"__builtins__": {}}))
    except (ArithmeticError, SyntaxError, ValueError) as exc:
        return f"error: {exc}"


@tool
def summarize_notes(notes: str, max_words: int = 120) -> str:
    """Ask for a bullet summary of raw research notes (truncated to max_words)."""
    words = notes.split()
    return " ".join(words[:max_words])


@tool
def search_documents(query: str, k: int = 6) -> str:
    """Search the user's indexed documents (uploaded in the Docs tab) for passages
    relevant to the query. Returns up to k passages, each prefixed by its source
    filename. Use this to ground research in the user's own material."""
    from genflow import rag

    hits = rag.search(query, k=k)
    if not hits:
        return "No documents indexed. Tell the user to upload files in the Docs tab first."
    return "\n\n".join(
        f"[{h.metadata.get('source', '?')}]\n{h.page_content}" for h in hits
    )


LOCAL_TOOLS = [calculator, summarize_notes, search_documents]
