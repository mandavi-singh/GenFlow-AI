import warnings

warnings.filterwarnings("ignore")

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("genflow-knowledge", log_level="ERROR")


@mcp.tool()
def search_knowledge_base(query: str) -> str:
    """Search the local GenFlow knowledge base for research material."""
    kb = {
        "langgraph": "LangGraph builds stateful agent graphs with nodes, edges and checkpointing.",
        "mcp": "Model Context Protocol (MCP) lets agents call external tools via a standard protocol.",
        "langchain": "LangChain composes LLM apps from chains, prompts, retrievers and tools.",
    }
    matches = [v for k, v in kb.items() if k in query.lower()]
    return "\n".join(matches) if matches else "No matching documents found."


@mcp.tool()
def save_note(title: str, content: str) -> str:
    """Persist a research note under data/notes."""
    import os
    from pathlib import Path

    data_dir = Path(os.getenv("GENFLOW_DATA_DIR", Path(__file__).resolve().parents[3] / "data"))
    path = data_dir / "notes"
    path.mkdir(parents=True, exist_ok=True)
    file = path / f"{title.replace(' ', '_')}.md"
    file.write_text(content, encoding="utf-8")
    return f"saved to {file}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
