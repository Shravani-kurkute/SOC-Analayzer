import time

import google.generativeai as genai

from app.ai.provider import AIProvider, AIResponse
from app.core.config import settings


class GeminiProvider(AIProvider):
    def __init__(self) -> None:
        genai.configure(api_key=settings.GEMINI_API_KEY or "")
        self.model = genai.GenerativeModel(
            settings.GEMINI_MODEL,
            generation_config={
                "temperature": settings.AI_TEMPERATURE,
                "max_output_tokens": settings.AI_MAX_TOKENS,
            },
        )

    async def generate(self, prompt: str, system_prompt: str | None = None) -> AIResponse:
        parts = []
        if system_prompt:
            parts.append(system_prompt)
        parts.append(prompt)

        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not configured")

        start = time.monotonic()
        response = await self.model.generate_content_async(parts, stream=False)
        elapsed = int((time.monotonic() - start) * 1000)

        return AIResponse(
            text=response.text,
            tokens_used=response.usage_metadata.total_tokens if response.usage_metadata else 0,
            latency_ms=elapsed,
        )
