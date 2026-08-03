import json as json_module
import time

import httpx

from app.ai.provider import AIProvider, AIResponse
from app.core.config import settings


class OllamaProvider(AIProvider):
    def __init__(self) -> None:
        self.base_url = settings.OLLAMA_BASE_URL.rstrip("/")
        self.model = settings.OLLAMA_MODEL
        self.client = httpx.AsyncClient(timeout=120.0)

    async def generate(self, prompt: str, system_prompt: str | None = None) -> AIResponse:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": f"{prompt}\n\nRespond with valid JSON only."})

        start = time.monotonic()
        response = await self.client.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": settings.AI_TEMPERATURE,
                    "num_predict": settings.AI_MAX_TOKENS,
                },
            },
        )
        elapsed = int((time.monotonic() - start) * 1000)

        if response.status_code != 200:
            raise ValueError(f"Ollama API error: {response.status_code} {response.text}")

        data = response.json()
        return AIResponse(
            text=data.get("message", {}).get("content", ""),
            tokens_used=data.get("eval_count", 0),
            latency_ms=elapsed,
        )
