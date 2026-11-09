"""A deterministic provider for tests and offline demos."""

from __future__ import annotations

from collections.abc import Sequence

from .base import LLMError


class FakeProvider:
    """Replays scripted replies in order and records every prompt it receives."""

    name = "fake"

    def __init__(self, replies: Sequence[str]) -> None:
        self._replies = list(replies)
        self.prompts: list[str] = []

    def complete(self, prompt: str, *, system: str | None = None) -> str:
        self.prompts.append(prompt)
        if not self._replies:
            raise LLMError("FakeProvider has no scripted replies left")
        return self._replies.pop(0)
