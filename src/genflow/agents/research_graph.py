from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import create_react_agent

from genflow.agents.state import ResearchState
from genflow.config import settings
from genflow.llm import ainvoke_with_retry, get_llm


async def researcher(state: ResearchState) -> dict:
    from genflow.mcp_tools.client import get_tools

    agent = create_react_agent(
        get_llm(),
        tools=await get_tools(),
        prompt=SystemMessage(
            "You are the Researcher. Use available tools to investigate the query, "
            "then hand back findings as a concise report. Prefer search_documents to "
            "ground your findings in the user's own indexed documents when they are "
            "relevant to the query. Use the calculator for any arithmetic. Hand back "
            "findings as a concise report."
        ),
    )
    result = None
    for attempt in range(3):
        try:
            result = await agent.ainvoke(
                {"messages": [HumanMessage(content=f"Research this: {state.query}")]}
            )
            break
        except Exception as exc:
            from genflow.llm import _is_transient

            if not _is_transient(exc) or attempt == 2:
                raise
            import asyncio

            await asyncio.sleep(2 * (2**attempt))
    return {"messages": result["messages"]}


async def writer(state: ResearchState) -> dict:
    llm = get_llm()
    context = "\n".join(
        m.content for m in state.messages[-6:] if isinstance(m, AIMessage) and m.content
    )
    critique_hint = f"\nAddress this critique: {state.critique}" if state.critique else ""
    reply = await ainvoke_with_retry(
        llm,
        [
            SystemMessage(
                "You are the Report Writer. Produce a clear final report from the research."
            ),
            HumanMessage(
                f"Query: {state.query}\n\nResearch:\n{context}{critique_hint}"
            ),
        ],
    )
    return {"messages": [reply], "report": reply.content, "revision_count": state.revision_count + 1}


async def critic(state: ResearchState) -> dict:
    llm = get_llm()
    reply = await ainvoke_with_retry(
        llm,
        [
            SystemMessage(
                "You are the Critic. Judge the report for accuracy, completeness and clarity."
                "Reply REJECT with one improvement request, or APPROVE if it is good."
            ),
            HumanMessage(f"Query: {state.query}\n\nReport:\n{state.report}"),
        ],
    )
    return {"messages": [reply], "critique": reply.content, "status": "working"}


def route_after_critic(state: ResearchState) -> str:
    approved = "approve" in state.critique.lower()
    if approved or state.revision_count > settings.max_revisions:
        return END
    return "writer"


def build_research_graph():
    g = StateGraph(ResearchState)
    g.add_node("researcher", researcher)
    g.add_node("writer", writer)
    g.add_node("critic", critic)
    g.add_edge(START, "researcher")
    g.add_edge("researcher", "writer")
    g.add_edge("writer", "critic")
    g.add_conditional_edges("critic", route_after_critic)
    return g.compile()
