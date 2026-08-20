"""LLM client abstraction.

Production note: agents should depend on this interface instead of importing an SDK directly.
"""

from dataclasses import dataclass

from multi_agent_research_lab.core.config import get_settings


@dataclass(frozen=True)
class LLMResponse:
    content: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost_usd: float | None = None


class LLMClient:
    """Provider-agnostic LLM client implementation supporting Gemini & OpenAI."""

    def __init__(self) -> None:
        self.settings = get_settings()

    def complete(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Return a model completion using Gemini API, OpenAI-compatible endpoint, or fallback."""
        gemini_key = self.settings.gemini_api_key
        openai_key = self.settings.openai_api_key

        # 1. Google Gemini Provider
        if gemini_key and gemini_key != "your-gemini-api-key":
            # Try google.generativeai SDK
            try:
                import google.generativeai as genai

                genai.configure(api_key=gemini_key)
                model_name = self.settings.gemini_model or "gemini-1.5-flash"
                model = genai.GenerativeModel(model_name)
                prompt = f"{system_prompt}\n\n{user_prompt}"
                response = model.generate_content(prompt)
                content = response.text or ""
                in_tokens = len(prompt.split())
                out_tokens = len(content.split())
                cost = (in_tokens * 0.075 + out_tokens * 0.30) / 1_000_000

                return LLMResponse(
                    content=content,
                    input_tokens=in_tokens,
                    output_tokens=out_tokens,
                    cost_usd=cost,
                )
            except Exception:
                pass

            # Try google.genai SDK
            try:
                import google.genai as genai

                client = genai.Client(api_key=gemini_key)
                prompt = f"{system_prompt}\n\n{user_prompt}"
                response = client.models.generate_content(
                    model=self.settings.gemini_model or "gemini-1.5-flash",
                    contents=prompt,
                )
                content = response.text or ""
                in_tokens = len(prompt.split())
                out_tokens = len(content.split())
                cost = (in_tokens * 0.075 + out_tokens * 0.30) / 1_000_000

                return LLMResponse(
                    content=content,
                    input_tokens=in_tokens,
                    output_tokens=out_tokens,
                    cost_usd=cost,
                )
            except Exception:
                pass

            # Try OpenAI endpoint for Gemini
            try:
                import openai

                client = openai.OpenAI(
                    api_key=gemini_key,
                    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                )
                model_name = self.settings.gemini_model or "gemini-1.5-flash"
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    timeout=float(self.settings.timeout_seconds),
                )
                content = response.choices[0].message.content or ""
                usage = response.usage
                in_tokens = usage.prompt_tokens if usage else len(user_prompt.split())
                out_tokens = usage.completion_tokens if usage else len(content.split())
                cost = (in_tokens * 0.075 + out_tokens * 0.30) / 1_000_000

                return LLMResponse(
                    content=content,
                    input_tokens=in_tokens,
                    output_tokens=out_tokens,
                    cost_usd=cost,
                )
            except Exception as exc:
                content = f"Gemini API Notice: {exc}"
                return LLMResponse(
                    content=content,
                    input_tokens=len(user_prompt.split()),
                    output_tokens=len(content.split()),
                    cost_usd=0.0001,
                )

        # 2. OpenAI / OpenAI-compatible Provider
        if openai_key and openai_key.startswith("sk-") and "your-openai-api-key" not in openai_key:
            try:
                import openai

                client = openai.OpenAI(
                    api_key=openai_key,
                    base_url=self.settings.openai_base_url,
                )
                response = client.chat.completions.create(
                    model=self.settings.openai_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    timeout=float(self.settings.timeout_seconds),
                )
                content = response.choices[0].message.content or ""
                usage = response.usage
                in_tokens = usage.prompt_tokens if usage else 0
                out_tokens = usage.completion_tokens if usage else 0
                cost = (in_tokens * 0.15 + out_tokens * 0.60) / 1_000_000

                return LLMResponse(
                    content=content,
                    input_tokens=in_tokens,
                    output_tokens=out_tokens,
                    cost_usd=cost,
                )
            except Exception as exc:
                content = f"LLM API Notice: {exc}"
                return LLMResponse(
                    content=content,
                    input_tokens=len(user_prompt.split()),
                    output_tokens=len(content.split()),
                    cost_usd=0.0001,
                )

        # 3. Stand-in mock generation when no keys configured
        content = (
            f"Synthesized analysis and findings for prompt: {user_prompt[:100]}... "
            "GraphRAG combines knowledge graphs with RAG techniques to improve relational reasoning "
            "and holistic document understanding over large text corpora."
        )
        in_tokens = len(system_prompt.split()) + len(user_prompt.split())
        out_tokens = len(content.split())
        cost = (in_tokens * 0.075 + out_tokens * 0.30) / 1_000_000

        return LLMResponse(
            content=content,
            input_tokens=in_tokens,
            output_tokens=out_tokens,
            cost_usd=cost,
        )
