"""Supervisor / router implementation."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState


class SupervisorAgent(BaseAgent):
    """Decides which worker should run next and when to stop."""

    name = "supervisor"

    def __init__(self) -> None:
        self.settings = get_settings()

    def run(self, state: ResearchState) -> ResearchState:
        """Update `state.route_history` with the next route."""
        max_iter = self.settings.max_iterations

        if state.iteration >= max_iter:
            next_route = "done"
        elif not state.sources or not state.research_notes:
            next_route = "researcher"
        elif not state.analysis_notes:
            next_route = "analyst"
        elif not state.final_answer:
            next_route = "writer"
        else:
            next_route = "done"

        state.record_route(next_route)
        state.agent_results.append(
            AgentResult(
                agent=AgentName.SUPERVISOR,
                content=f"Routing decision: {next_route} (iteration {state.iteration})",
                metadata={"next_route": next_route, "iteration": state.iteration},
            )
        )
        state.add_trace_event("supervisor_routing", {"next": next_route, "iteration": state.iteration})

        return state
