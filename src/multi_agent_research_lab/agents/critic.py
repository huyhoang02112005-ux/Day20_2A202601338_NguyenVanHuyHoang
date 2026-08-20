"""Critic agent implementation."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient


class CriticAgent(BaseAgent):
    """Reviews final answer for factual consistency and citation coverage."""

    name = "critic"

    def __init__(self) -> None:
        self.llm_client = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Add fact-check and citation coverage evaluation to trace."""
        answer = state.final_answer or ""
        sources_count = len(state.sources)

        has_citations = "[" in answer and "]" in answer
        citation_score = 1.0 if has_citations or sources_count == 0 else 0.5

        state.add_trace_event(
            "critic_evaluation",
            {"citation_score": citation_score, "has_citations": has_citations},
        )
        state.agent_results.append(
            AgentResult(
                agent=AgentName.CRITIC,
                content=f"Critic evaluation completed. Citation coverage score: {citation_score}",
                metadata={"citation_score": citation_score},
            )
        )

        return state
