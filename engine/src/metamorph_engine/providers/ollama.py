"""Adapter for a local Ollama server (`/api/generate`, non-streaming)."""

from __future__ import annotations

import httpx

from .base import LLMError


class OllamaProvider:
    """Talks to Ollama over HTTP."""

    def __init__(
        self,
        base_url: str,
        model: str,
        *,
        timeout_s: float = 120.0,
        client: httpx.Client | None = None,
    ) -> None:
        self.name = f"ollama:{model}"
        self._url = f"{base_url.rstrip('/')}/api/generate"
        self._model = model
        self._client = client or httpx.Client(timeout=timeout_s)

    def complete(self, prompt: str, *, system: str | None = None) -> str:
        payload: dict[str, object] = {
            "model": self._model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2},
        }
        if system:
            payload["system"] = system
        try:
            response = self._client.post(self._url, json=payload)
            response.raise_for_status()
            data = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise LLMError(f"Ollama request failed: {exc}") from exc
        text = data.get("response") if isinstance(data, dict) else None
        if not isinstance(text, str) or not text.strip():
            raise LLMError("Ollama returned no text in 'response'")
        return text
