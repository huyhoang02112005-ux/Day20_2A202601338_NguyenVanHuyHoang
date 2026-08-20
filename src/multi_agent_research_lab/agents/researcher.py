"""Researcher agent implementation."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.services.search_client import SearchClient


class ResearcherAgent(BaseAgent):
    """Collects sources and creates concise research notes."""

    name = "researcher"

    def __init__(self) -> None:
        self.search_client = SearchClient()
        self.llm_client = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.sources` and `state.research_notes`."""
        query = state.request.query
        max_sources = state.request.max_sources

        # 1. Fetch sources
        fetched_sources = self.search_client.search(query=query, max_results=max_sources)
        state.sources.extend(fetched_sources)

        # 2. Synthesize research notes via LLM
        source_texts = "\n\n".join(
            [f"[{idx + 1}] Title: {s.title}\nSnippet: {s.snippet}" for idx, s in enumerate(state.sources)]
        )
        system_prompt = (
            "You are a meticulous Researcher Agent. Summarize key factual evidence and claims "
            "from the provided sources relevant to the query."
        )
        user_prompt = f"Query: {query}\n\nSources:\n{source_texts}"

        llm_resp = self.llm_client.complete(system_prompt=system_prompt, user_prompt=user_prompt)
        state.research_notes = llm_resp.content

        # 3. Record trace & result
        result_content = f"Retrieved {len(fetched_sources)} sources and compiled research notes."
        state.agent_results.append(
            AgentResult(
                agent=AgentName.RESEARCHER,
                content=result_content,
                metadata={"sources_count": len(fetched_sources), "tokens": llm_resp.output_tokens},
            )
        )
        state.add_trace_event("researcher_complete", {"sources_count": len(fetched_sources)})

        return state
