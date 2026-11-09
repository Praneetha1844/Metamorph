"""Model backends behind the `LLMProvider` interface."""

from __future__ import annotations

from ..config import Settings
from .base import LLMError, LLMProvider
from .fake import FakeProvider
from .ollama import OllamaProvider
from .openai_compat import OpenAICompatProvider


def build_provider(settings: Settings) -> LLMProvider:
    """Create the provider named in `settings`."""
    if settings.provider == "openai":
        return OpenAICompatProvider(
            settings.openai_base_url, settings.openai_model, settings.openai_api_key
        )
    return OllamaProvider(settings.ollama_url, settings.ollama_model)


__all__ = [
    "FakeProvider",
    "LLMError",
    "LLMProvider",
    "OllamaProvider",
    "OpenAICompatProvider",
    "build_provider",
]
