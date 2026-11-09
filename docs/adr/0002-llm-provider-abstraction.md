# ADR 0002: A small provider interface for model backends

Status: accepted

## Context

The original UI called a local Ollama server directly. The engine needs to run against Ollama, hosted OpenAI-compatible endpoints, and a deterministic stand-in for tests, without the pipeline knowing which.

## Decision

Define a `Protocol` with one method:

```python
class LLMProvider(Protocol):
    name: str
    def complete(self, prompt: str, *, system: str | None = None) -> str: ...
```

Adapters: `OllamaProvider` (`/api/generate`), `OpenAICompatProvider` (`/chat/completions`), and `FakeProvider`, which replays scripted replies and records prompts. Every backend failure (network, HTTP status, malformed JSON, empty text) is raised as `LLMError`; the pipeline converts it to the `provider_error` verdict.

Adapters accept an injected `httpx.Client`, so tests use `httpx.MockTransport` and never touch the network.

## Consequences

- The pipeline is testable end to end with no model and no network.
- Adding a backend means one small class.
- Text in, text out is deliberately minimal: no streaming, tool calls, token accounting or structured output. The reply is parsed for a fenced code block.
- No retry or backoff inside adapters; the pipeline's attempt loop is the only retry mechanism.
- Sampling is fixed at temperature 0.2. It is not configurable yet.

## Revisit when

Streaming responses to the UI, cost or token tracking, or structured output (JSON schema) is needed.
