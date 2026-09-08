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


LOCAL_TOOLS = [calculator, summarize_notes]
