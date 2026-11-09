"""Isolated test execution."""

from __future__ import annotations

from ..config import Settings
from .base import Sandbox, SandboxError
from .docker_runner import DockerSandbox
from .subprocess_runner import SubprocessSandbox


def build_sandbox(settings: Settings) -> Sandbox:
    """Create the sandbox named in `settings`."""
    if settings.sandbox == "docker":
        return DockerSandbox(
            settings.docker_image,
            timeout_s=settings.test_timeout_s + 10,
            memory_mb=settings.memory_mb,
        )
    return SubprocessSandbox(timeout_s=settings.test_timeout_s, memory_mb=settings.memory_mb)


__all__ = ["DockerSandbox", "Sandbox", "SandboxError", "SubprocessSandbox", "build_sandbox"]
