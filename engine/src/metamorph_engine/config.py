"""Runtime settings, read from `METAMORPH_*` environment variables."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, field


class ConfigError(ValueError):
    """Raised when an environment variable holds an unusable value."""


def _int(env: Mapping[str, str], key: str, default: int, *, minimum: int = 1) -> int:
    raw = env.get(key)
    if raw is None or raw == "":
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise ConfigError(f"{key} must be an integer, got {raw!r}") from exc
    if value < minimum:
        raise ConfigError(f"{key} must be >= {minimum}, got {value}")
    return value


@dataclass(frozen=True)
class Settings:
    """All tunables for the service. Defaults are safe for local use."""

    provider: str = "ollama"
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "codellama"
    openai_base_url: str = "https://api.openai.com/v1"
    openai_api_key: str = ""
    openai_model: str = ""
    max_attempts: int = 3
    test_timeout_s: int = 10
    memory_mb: int = 512
    sandbox: str = "subprocess"
    docker_image: str = "metamorph-sandbox:latest"
    max_concurrent_runs: int = 2
    cors_origins: tuple[str, ...] = field(
        default_factory=lambda: ("http://localhost:5173", "http://127.0.0.1:5173")
    )

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> Settings:
        """Build settings from `env` (defaults to `os.environ`), validating every value."""
        e = os.environ if env is None else env
        provider = e.get("METAMORPH_PROVIDER", cls.provider).lower()
        if provider not in {"ollama", "openai"}:
            raise ConfigError(f"METAMORPH_PROVIDER must be 'ollama' or 'openai', got {provider!r}")
        sandbox = e.get("METAMORPH_SANDBOX", cls.sandbox).lower()
        if sandbox not in {"subprocess", "docker"}:
            raise ConfigError(
                f"METAMORPH_SANDBOX must be 'subprocess' or 'docker', got {sandbox!r}"
            )
        openai_model = e.get("METAMORPH_OPENAI_MODEL", "")
        if provider == "openai" and not openai_model:
            raise ConfigError("METAMORPH_OPENAI_MODEL is required when METAMORPH_PROVIDER=openai")
        origins = tuple(
            o.strip() for o in e.get("METAMORPH_CORS_ORIGINS", "").split(",") if o.strip()
        ) or cls().cors_origins
        return cls(
            provider=provider,
            ollama_url=e.get("METAMORPH_OLLAMA_URL", cls.ollama_url).rstrip("/"),
            ollama_model=e.get("METAMORPH_OLLAMA_MODEL", cls.ollama_model),
            openai_base_url=e.get("METAMORPH_OPENAI_BASE_URL", cls.openai_base_url).rstrip("/"),
            openai_api_key=e.get("METAMORPH_OPENAI_API_KEY", ""),
            openai_model=openai_model,
            max_attempts=_int(e, "METAMORPH_MAX_ATTEMPTS", cls.max_attempts),
            test_timeout_s=_int(e, "METAMORPH_TEST_TIMEOUT_S", cls.test_timeout_s),
            memory_mb=_int(e, "METAMORPH_MEMORY_MB", cls.memory_mb, minimum=64),
            sandbox=sandbox,
            docker_image=e.get("METAMORPH_DOCKER_IMAGE", cls.docker_image),
            max_concurrent_runs=_int(e, "METAMORPH_MAX_CONCURRENT_RUNS", cls.max_concurrent_runs),
            cors_origins=origins,
        )
