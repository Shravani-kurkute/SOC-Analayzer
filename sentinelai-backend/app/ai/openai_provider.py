import time

from openai import AsyncOpenAI

from app.ai.provider import AIProvider, AIResponse
from app.core.config import settings


class OpenAIProvider(AIProvider):
    def __init__(self) -> None:
        client_kwargs = {"api_key": settings.OPENAI_API_KEY}
        if settings.OPENAI_ORG_ID:
            client_kwargs["organization"] = settings.OPENAI_ORG_ID
        self.client = AsyncOpenAI(**client_kwargs)
        self.model = settings.OPENAI_MODEL

    async def generate(self, prompt: str, system_prompt: str | None = None) -> AIResponse:
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not configured")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        start = time.monotonic()
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=settings.AI_TEMPERATURE,
            max_tokens=settings.AI_MAX_TOKENS,
            response_format={"type": "json_object"},
        )
        elapsed = int((time.monotonic() - start) * 1000)

        choice = response.choices[0]
        return AIResponse(
            text=choice.message.content or "",
            tokens_used=response.usage.total_tokens if response.usage else 0,
            latency_ms=elapsed,
        )
