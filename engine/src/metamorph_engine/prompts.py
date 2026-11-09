"""Prompt construction and extraction of code from model replies."""

from __future__ import annotations

import ast
import re

SYSTEM_PROMPT = (
    "You are a careful Python refactoring assistant. Improve readability and structure "
    "without changing behaviour. Keep every public name, signature and return value that "
    "existing callers may rely on. Reply with the complete refactored module in a single "
    "```python fenced block and nothing else."
)

_FENCE = re.compile(r"```(?:python|py)?[ \t]*\n(.*?)```", re.DOTALL | re.IGNORECASE)


def build_prompt(
    source: str,
    *,
    instructions: str | None = None,
    previous_candidate: str | None = None,
    failure_output: str | None = None,
) -> str:
    """Build the user prompt, including failure feedback when retrying."""
    parts = ["Refactor this Python module.", f"```python\n{source}\n```"]
    if instructions:
        parts.append(f"Additional instructions: {instructions}")
    if previous_candidate is not None and failure_output is not None:
        parts.append(
            "Your previous refactor failed the original tests. Fix it. Previous attempt:\n"
            f"```python\n{previous_candidate}\n```\nTest output:\n```\n{failure_output}\n```"
        )
    return "\n\n".join(parts)


def extract_code(reply: str) -> str | None:
    """Return the first fenced code block, or the whole reply if it is itself valid Python.

    Returns None when neither applies, so the caller can record a failed attempt.
    """
    match = _FENCE.search(reply)
    if match:
        return match.group(1).strip("\n") + "\n"
    stripped = reply.strip()
    if not stripped:
        return None
    try:
        ast.parse(stripped)
    except SyntaxError:
        return None
    return stripped + "\n"
