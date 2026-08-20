"""Command-line entrypoint for the lab starter."""

from typing import Annotated

import typer
from pydantic import ValidationError
from rich.console import Console
from rich.panel import Panel

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow
from multi_agent_research_lab.observability.logging import configure_logging

app = typer.Typer(help="Multi-Agent Research Lab starter CLI")
console = Console()


from multi_agent_research_lab.observability.tracing import init_tracing


def _init() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    init_tracing()


def _parse_query(query: str) -> ResearchQuery:
    try:
        return ResearchQuery(query=query)
    except ValidationError as exc:
        console.print(
            Panel.fit(
                f"Invalid query: {exc.errors()[0]['msg']}",
                title="Input Error",
                style="red",
            )
        )
        raise typer.Exit(code=1) from exc


from time import perf_counter
from multi_agent_research_lab.services.llm_client import LLMClient


@app.command()
def baseline(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run a minimal single-agent baseline implementation."""

    _init()
    request = _parse_query(query)
    state = ResearchState(request=request)

    llm = LLMClient()
    start_time = perf_counter()
    response = llm.complete(
        system_prompt=(
            "You are a baseline research assistant. Answer the user query comprehensively "
            "with facts, analysis, and a structured conclusion."
        ),
        user_prompt=request.query,
    )
    elapsed = perf_counter() - start_time

    state.final_answer = response.content
    state.add_trace_event(
        "baseline_llm_call",
        {
            "latency_seconds": elapsed,
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
            "cost_usd": response.cost_usd,
        },
    )

    console.print(Panel.fit(state.final_answer, title="Single-Agent Baseline Result"))
    console.print(
        f"[dim]Latency: {elapsed:.2f}s | Input Tokens: {response.input_tokens} | "
        f"Output Tokens: {response.output_tokens} | Cost: ${response.cost_usd:.6f}[/dim]"
    )



@app.command("multi-agent")
def multi_agent(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run the multi-agent workflow skeleton."""

    _init()
    state = ResearchState(request=_parse_query(query))
    workflow = MultiAgentWorkflow()
    try:
        result = workflow.run(state)
    except StudentTodoError as exc:
        console.print(Panel.fit(str(exc), title="Expected TODO", style="yellow"))
        raise typer.Exit(code=2) from exc
    console.print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    app()
