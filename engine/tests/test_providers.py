"""Provider adapters, exercised with httpx's in-memory transport (no network)."""

from __future__ import annotations

import json

import httpx
import pytest

from metamorph_engine.config import Settings
from metamorph_engine.providers import (
    FakeProvider,
    LLMError,
    OllamaProvider,
    OpenAICompatProvider,
    build_provider,
)


def _client(transport: httpx.MockTransport) -> httpx.Client:
    return httpx.Client(transport=transport)


def test_ollama_sends_prompt_and_returns_text() -> None:
    seen: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen.update(json.loads(request.content))
        seen["path"] = request.url.path
        return httpx.Response(200, json={"response": "hello"})

    provider = OllamaProvider("http://x", "m", client=_client(httpx.MockTransport(handler)))
    assert provider.complete("p", system="s") == "hello"
    assert seen["path"] == "/api/generate"
    assert seen["model"] == "m"
    assert seen["stream"] is False
    assert seen["system"] == "s"


@pytest.mark.parametrize("body", [{}, {"response": "  "}, {"response": 3}])
def test_ollama_rejects_unusable_bodies(body: dict[str, object]) -> None:
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json=body))
    with pytest.raises(LLMError):
        OllamaProvider("http://x", "m", client=_client(transport)).complete("p")


def test_ollama_wraps_http_errors() -> None:
    transport = httpx.MockTransport(lambda request: httpx.Response(500, text="boom"))
    with pytest.raises(LLMError):
        OllamaProvider("http://x", "m", client=_client(transport)).complete("p")


def test_openai_compat_builds_chat_request() -> None:
    seen: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["auth"] = request.headers.get("authorization")
        seen["body"] = json.loads(request.content)
        return httpx.Response(200, json={"choices": [{"message": {"content": "ok"}}]})

    provider = OpenAICompatProvider(
        "http://x/v1", "gpt", "k", client=_client(httpx.MockTransport(handler))
    )
    assert provider.complete("hi", system="sys") == "ok"
    assert seen["auth"] == "Bearer k"
    body = seen["body"]
    assert isinstance(body, dict)
    assert [m["role"] for m in body["messages"]] == ["system", "user"]


def test_openai_compat_requires_model_and_valid_shape() -> None:
    with pytest.raises(LLMError):
        OpenAICompatProvider("http://x", "")
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json={"choices": []}))
    with pytest.raises(LLMError):
        OpenAICompatProvider("http://x", "m", client=_client(transport)).complete("p")


def test_fake_provider_replays_in_order_then_errors() -> None:
    fake = FakeProvider(["a", "b"])
    assert fake.complete("1") == "a"
    assert fake.complete("2") == "b"
    assert fake.prompts == ["1", "2"]
    with pytest.raises(LLMError):
        fake.complete("3")


def test_build_provider_honours_settings() -> None:
    assert build_provider(Settings()).name == "ollama:codellama"
    chosen = build_provider(Settings(provider="openai", openai_model="m"))
    assert chosen.name == "openai-compat:m"
