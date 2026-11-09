"""Adapter for any OpenAI-compatible `/chat/completions` endpoint."""

from __future__ import annotations

import httpx

from .base import LLMError


class OpenAICompatProvider:
    """Talks to an OpenAI-compatible chat API. The key is sent only as a bearer header."""

    def __init__(
        self,
        base_url: str,
        model: str,
        api_key: str = "",
        *,
        timeout_s: float = 120.0,
        client: httpx.Client | None = None,
    ) -> None:
        if not model:
            raise LLMError("An OpenAI-compatible provider needs a model name")
        self.name = f"openai-compat:{model}"
        self._url = f"{base_url.rstrip('/')}/chat/completions"
        self._model = model
        self._headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        self._client = client or httpx.Client(timeout=timeout_s)

    def complete(self, prompt: str, *, system: str | None = None) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        body = {"model": self._model, "messages": messages, "temperature": 0.2}
        try:
            response = self._client.post(self._url, json=body, headers=self._headers)
            response.raise_for_status()
            data = response.json()
            text = data["choices"][0]["message"]["content"]
        except (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError) as exc:
            raise LLMError(f"OpenAI-compatible request failed: {exc}") from exc
        if not isinstance(text, str) or not text.strip():
            raise LLMError("The chat endpoint returned an empty message")
        return text
