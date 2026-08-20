"""Writer agent implementation."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient


class WriterAgent(BaseAgent):
    """Produces final answer from research and analysis notes."""

    name = "writer"

    def __init__(self) -> None:
        self.llm_client = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.final_answer`."""
        query = state.request.query
        audience = state.request.audience
        analysis = state.analysis_notes or "No analysis notes."
        sources_list = "\n".join(
            [f"[{i + 1}] {s.title} ({s.url or 'N/A'})" for i, s in enumerate(state.sources)]
        )

        system_prompt = (
            f"You are an expert Technical Writer Agent writing for {audience}. "
            "Synthesize the analysis and sources into a clear, comprehensive final answer. "
            "Include inline citations such as [1], [2] pointing to the provided sources list."
        )
        user_prompt = (
            f"Query: {query}\n\n"
            f"Analysis Notes:\n{analysis}\n\n"
            f"Sources:\n{sources_list or 'No explicit sources'}"
        )

        llm_resp = self.llm_client.complete(system_prompt=system_prompt, user_prompt=user_prompt)

        # Append references section if not present
        final_text = llm_resp.content
        if state.sources and "References" not in final_text:
            final_text += "\n\n### References\n" + sources_list

        state.final_answer = final_text

        state.agent_results.append(
            AgentResult(
                agent=AgentName.WRITER,
                content="Final report generated.",
                metadata={"answer_length": len(final_text)},
            )
        )
        state.add_trace_event("writer_complete", {"answer_length": len(final_text)})

        return state
