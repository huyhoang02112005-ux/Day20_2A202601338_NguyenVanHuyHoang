"""Tracing hooks and observability telemetry."""

import os
from collections.abc import Iterator
from contextlib import contextmanager
from time import perf_counter
from typing import Any

from multi_agent_research_lab.core.config import get_settings


def init_tracing() -> None:
    """Initialize environment variables for LangSmith or Langfuse tracing."""
    settings = get_settings()

    # LangSmith automatic tracing integration
    if settings.langsmith_api_key:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = settings.langsmith_api_key
        os.environ["LANGSMITH_API_KEY"] = settings.langsmith_api_key
        os.environ["LANGCHAIN_PROJECT"] = settings.langsmith_project

    # Langfuse tracing integration
    if settings.langfuse_public_key and settings.langfuse_secret_key:
        os.environ["LANGFUSE_PUBLIC_KEY"] = settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = settings.langfuse_secret_key
        os.environ["LANGFUSE_HOST"] = settings.langfuse_host


@contextmanager
def trace_span(name: str, attributes: dict[str, Any] | None = None) -> Iterator[dict[str, Any]]:
    """Span context supporting local traces and optional LangSmith / Langfuse hooks."""
    settings = get_settings()
    started = perf_counter()
    span: dict[str, Any] = {
        "name": name,
        "attributes": attributes or {},
        "duration_seconds": None,
        "langsmith_project": settings.langsmith_project if settings.langsmith_api_key else None,
        "langfuse_host": settings.langfuse_host if settings.langfuse_public_key else None,
    }

    try:
        yield span
    finally:
        span["duration_seconds"] = perf_counter() - started
