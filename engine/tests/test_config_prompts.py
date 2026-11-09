"""Settings parsing and prompt helpers."""

from __future__ import annotations

import pytest

from metamorph_engine.config import ConfigError, Settings
from metamorph_engine.prompts import build_prompt, extract_code


def test_defaults_when_env_is_empty() -> None:
    settings = Settings.from_env({})
    assert settings.provider == "ollama"
    assert settings.max_attempts == 3
    assert settings.max_concurrent_runs == 2
    assert settings.cors_origins == ("http://localhost:5173", "http://127.0.0.1:5173")


def test_env_overrides_and_trailing_slash_is_stripped() -> None:
    settings = Settings.from_env(
        {
            "METAMORPH_PROVIDER": "OpenAI",
            "METAMORPH_OPENAI_MODEL": "some-model",
            "METAMORPH_OPENAI_BASE_URL": "http://h/v1/",
            "METAMORPH_MAX_ATTEMPTS": "5",
            "METAMORPH_CORS_ORIGINS": "http://a, http://b",
        }
    )
    assert settings.provider == "openai"
    assert settings.openai_base_url == "http://h/v1"
    assert settings.max_attempts == 5
    assert settings.cors_origins == ("http://a", "http://b")


@pytest.mark.parametrize(
    "env",
    [
        {"METAMORPH_PROVIDER": "gpt"},
        {"METAMORPH_SANDBOX": "vm"},
        {"METAMORPH_MAX_ATTEMPTS": "zero"},
        {"METAMORPH_MAX_ATTEMPTS": "0"},
        {"METAMORPH_MEMORY_MB": "8"},
        {"METAMORPH_MAX_CONCURRENT_RUNS": "0"},
        {"METAMORPH_PROVIDER": "openai"},  # the model name is required
    ],
)
def test_bad_values_raise_config_error(env: dict[str, str]) -> None:
    with pytest.raises(ConfigError):
        Settings.from_env(env)


def test_extract_code_prefers_fenced_block() -> None:
    assert extract_code("text\n```python\nx = 1\n```\nmore") == "x = 1\n"
    assert extract_code("```\ny = 2\n```") == "y = 2\n"


def test_extract_code_accepts_bare_python_only_if_it_parses() -> None:
    assert extract_code("z = 3") == "z = 3\n"
    assert extract_code("Sure, here is the thing") is None
    assert extract_code("   ") is None


def test_build_prompt_includes_feedback_only_on_retry() -> None:
    first = build_prompt("a = 1\n", instructions="keep it short")
    assert "keep it short" in first
    assert "previous refactor" not in first
    retry = build_prompt("a = 1\n", previous_candidate="a = 2\n", failure_output="boom")
    assert "failed the original tests" in retry
    assert "boom" in retry


def test_extract_code_skips_empty_fenced_blocks() -> None:
    reply = "```python\n\n```\ntext\n```python\nx = 1\n```"
    assert extract_code(reply) == "x = 1\n"
    assert extract_code("```python\n```") is None
