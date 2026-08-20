"""LangGraph workflow implementation."""

from typing import Any

from multi_agent_research_lab.agents.analyst import AnalystAgent
from multi_agent_research_lab.agents.critic import CriticAgent
from multi_agent_research_lab.agents.researcher import ResearcherAgent
from multi_agent_research_lab.agents.supervisor import SupervisorAgent
from multi_agent_research_lab.agents.writer import WriterAgent
from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.state import ResearchState


class MultiAgentWorkflow:
    """Builds and runs the multi-agent graph orchestration workflow."""

    def __init__(self) -> None:
        self.supervisor = SupervisorAgent()
        self.researcher = ResearcherAgent()
        self.analyst = AnalystAgent()
        self.writer = WriterAgent()
        self.critic = CriticAgent()
        self.settings = get_settings()

    def build(self) -> Any:
        """Create a LangGraph StateGraph instance if langgraph is available, else fallback runner."""
        try:
            from langgraph.graph import END, START, StateGraph

            workflow = StateGraph(ResearchState)

            # Define node functions
            workflow.add_node("supervisor", lambda state: self.supervisor.run(state))
            workflow.add_node("researcher", lambda state: self.researcher.run(state))
            workflow.add_node("analyst", lambda state: self.analyst.run(state))
            workflow.add_node("writer", lambda state: self.writer.run(state))
            workflow.add_node("critic", lambda state: self.critic.run(state))

            # Entrypoint
            workflow.add_edge(START, "supervisor")

            # Conditional routing from supervisor
            def route_decision(state: ResearchState) -> str:
                if not state.route_history:
                    return "done"
                last_route = state.route_history[-1]
                if last_route == "done":
                    return END
                return last_route

            workflow.add_conditional_edges(
                "supervisor",
                route_decision,
                {
                    "researcher": "researcher",
                    "analyst": "analyst",
                    "writer": "writer",
                    END: END,
                },
            )

            # Workers always loop back to supervisor
            workflow.add_edge("researcher", "supervisor")
            workflow.add_edge("analyst", "supervisor")
            workflow.add_edge("writer", "critic")
            workflow.add_edge("critic", "supervisor")

            return workflow.compile()
        except ImportError:
            return None

    def run(self, state: ResearchState) -> ResearchState:
        """Execute the multi-agent graph workflow and return final state."""
        app = self.build()
        if app is not None:
            try:
                result = app.invoke(state)
                if isinstance(result, ResearchState):
                    return result
                elif isinstance(result, dict):
                    return ResearchState(**result)
            except Exception:
                pass  # Fall back to state machine loop if graph invoke encounters format mismatch

        # Robust State Machine Execution Loop
        max_iterations = self.settings.max_iterations
        while state.iteration < max_iterations:
            state = self.supervisor.run(state)
            last_route = state.route_history[-1] if state.route_history else "done"

            if last_route == "done":
                break
            elif last_route == "researcher":
                state = self.researcher.run(state)
            elif last_route == "analyst":
                state = self.analyst.run(state)
            elif last_route == "writer":
                state = self.writer.run(state)
                state = self.critic.run(state)
            else:
                break

        return state
