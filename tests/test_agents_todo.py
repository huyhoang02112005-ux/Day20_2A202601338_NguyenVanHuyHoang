"""Unit tests for individual agent runs."""

from multi_agent_research_lab.agents.analyst import AnalystAgent
from multi_agent_research_lab.agents.critic import CriticAgent
from multi_agent_research_lab.agents.researcher import ResearcherAgent
from multi_agent_research_lab.agents.writer import WriterAgent
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState


def test_researcher_agent_run() -> None:
    agent = ResearcherAgent()
    state = ResearchState(request=ResearchQuery(query="GraphRAG architecture"))
    state = agent.run(state)
    assert len(state.sources) > 0
    assert state.research_notes is not None


def test_analyst_agent_run() -> None:
    agent = AnalystAgent()
    state = ResearchState(request=ResearchQuery(query="GraphRAG architecture"))
    state.research_notes = "Found 3 sources on GraphRAG KGs and LLM synthesis."
    state = agent.run(state)
    assert state.analysis_notes is not None


def test_writer_and_critic_agent_run() -> None:
    writer = WriterAgent()
    critic = CriticAgent()
    state = ResearchState(request=ResearchQuery(query="GraphRAG architecture"))
    state.analysis_notes = "GraphRAG integrates KGs with LLM RAG."
    state = writer.run(state)
    assert state.final_answer is not None

    state = critic.run(state)
    assert len(state.agent_results) > 0
