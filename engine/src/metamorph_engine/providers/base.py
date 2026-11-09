"""The provider interface every model backend implements."""

from __future__ import annotations

from typing import Protocol


class LLMError(RuntimeError):
    """The model backend was unreachable or returned an unusable response."""


class LLMProvider(Protocol):
    """A text-in, text-out model backend."""

    name: str

    def complete(self, prompt: str, *, system: str | None = None) -> str:
        """Return the model's reply to `prompt`. Raises `LLMError` on any backend failure."""
        ...
