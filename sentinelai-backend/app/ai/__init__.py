from app.ai.provider import AIProvider, AIResponse
from app.ai.gemini_provider import GeminiProvider
from app.ai.openai_provider import OpenAIProvider
from app.ai.ollama_provider import OllamaProvider

__all__ = ["AIProvider", "AIResponse", "GeminiProvider", "OpenAIProvider", "OllamaProvider"]


def get_provider(provider_name: str | None = None) -> AIProvider:
    from app.core.config import settings

    name = (provider_name or settings.AI_PROVIDER).lower()
    providers = {
        "gemini": GeminiProvider,
        "openai": OpenAIProvider,
        "ollama": OllamaProvider,
    }
    cls = providers.get(name)
    if not cls:
        raise ValueError(f"Unknown AI provider: {name}. Supported: {', '.join(providers)}")
    return cls()
