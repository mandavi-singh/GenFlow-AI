from genflow.agents.research_graph import build_research_graph, route_after_critic
from genflow.agents.state import ResearchState


def test_graph_compiles():
    graph = build_research_graph()
    assert graph is not None


def test_route_ends_on_approval():
    state = ResearchState(query="q", report="r", critique="APPROVE: looks good")
    assert route_after_critic(state) == "__end__"


def test_route_revises_on_rejection():
    state = ResearchState(query="q", report="r", critique="REJECT: add citations")
    assert route_after_critic(state) == "writer"


def test_route_stops_after_max_revisions():
    state = ResearchState(
        query="q", report="r", critique="REJECT", revision_count=99, status="working"
    )
    assert route_after_critic(state) == "__end__"
