"""Unit tests for agents and multi-agent workflow."""

from multi_agent_research_lab.agents.supervisor import SupervisorAgent
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow
from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.services.search_client import SearchClient


def test_llm_client_complete() -> None:
    client = LLMClient()
    response = client.complete("System prompt", "User query test")
    assert response.content
    assert response.input_tokens is not None
    assert response.output_tokens is not None


def test_search_client_search() -> None:
    client = SearchClient()
    docs = client.search("GraphRAG state of the art", max_results=3)
    assert len(docs) > 0
    assert docs[0].title
    assert docs[0].snippet


def test_supervisor_routing() -> None:
    supervisor = SupervisorAgent()
    state = ResearchState(request=ResearchQuery(query="Explain multi-agent systems"))

    # Initial state -> Should route to researcher
    state = supervisor.run(state)
    assert state.route_history[-1] == "researcher"
    assert state.iteration == 1


def test_multi_agent_workflow_execution() -> None:
    workflow = MultiAgentWorkflow()
    initial_state = ResearchState(request=ResearchQuery(query="Research GraphRAG state-of-the-art"))

    final_state = workflow.run(initial_state)

    assert final_state.final_answer is not None
    assert len(final_state.sources) > 0
    assert final_state.research_notes is not None
    assert final_state.analysis_notes is not None
    assert "researcher" in final_state.route_history
    assert "analyst" in final_state.route_history
    assert "writer" in final_state.route_history
