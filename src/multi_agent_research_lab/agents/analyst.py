"""Analyst agent implementation."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient


class AnalystAgent(BaseAgent):
    """Turns research notes into structured insights."""

    name = "analyst"

    def __init__(self) -> None:
        self.llm_client = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.analysis_notes`."""
        research_notes = state.research_notes or "No research notes collected."
        query = state.request.query

        system_prompt = (
            "You are a critical Analyst Agent. Analyze the research notes, extract key claims, "
            "evaluate evidence strength, contrast viewpoints, and draw analytical conclusions."
        )
        user_prompt = f"Query: {query}\n\nResearch Notes:\n{research_notes}"

        llm_resp = self.llm_client.complete(system_prompt=system_prompt, user_prompt=user_prompt)
        state.analysis_notes = llm_resp.content

        state.agent_results.append(
            AgentResult(
                agent=AgentName.ANALYST,
                content="Structured analysis completed.",
                metadata={"analysis_length": len(state.analysis_notes)},
            )
        )
        state.add_trace_event("analyst_complete", {"length": len(state.analysis_notes)})

        return state
