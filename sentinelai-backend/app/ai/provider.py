from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class AIResponse:
    text: str
    tokens_used: int = 0
    latency_ms: int = 0


class AIProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str | None = None) -> AIResponse:
        ...
