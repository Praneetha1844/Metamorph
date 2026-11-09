"""Optional sandbox: run the suite in a locked-down, network-less Docker container.

Written against the Docker CLI and the image in `engine/docker/sandbox.Dockerfile`. It is
opt-in (`METAMORPH_SANDBOX=docker`); the engine does not require Docker to be installed.
"""

from __future__ import annotations

import subprocess
import tempfile
import time
from pathlib import Path
from uuid import uuid4

from ..models import SuiteResult
from .base import TESTS_FILENAME, SandboxError, build_result, write_workspace


class DockerSandbox:
    """Runs pytest inside a container with no network, a read-only root and capped resources."""

    name = "docker"

    def __init__(
        self,
        image: str = "metamorph-sandbox:latest",
        *,
        timeout_s: float = 20.0,
        memory_mb: int = 256,
        cpus: float = 1.0,
        pids_limit: int = 128,
        docker_bin: str = "docker",
    ) -> None:
        if timeout_s <= 0 or memory_mb < 64 or cpus <= 0 or pids_limit < 16:
            raise ValueError("invalid sandbox limits")
        self._image = image
        self._timeout_s = timeout_s
        self._memory_mb = memory_mb
        self._cpus = cpus
        self._pids_limit = pids_limit
        self._docker = docker_bin

    def run_tests(self, source: str, tests: str, module_name: str) -> SuiteResult:
        container = f"metamorph-{uuid4().hex[:12]}"
        with tempfile.TemporaryDirectory(prefix="metamorph-") as directory:
            root = Path(directory)
            write_workspace(root, source, tests, module_name)
            command = [
                self._docker, "run", "--rm", "--name", container,
                "--network", "none",
                "--memory", f"{self._memory_mb}m",
                "--cpus", str(self._cpus),
                "--pids-limit", str(self._pids_limit),
                "--read-only", "--tmpfs", "/tmp:rw,size=64m",
                "--cap-drop", "ALL",
                "--security-opt", "no-new-privileges",
                "-v", f"{root}:/work:ro", "-w", "/work",
                self._image,
                "python", "-m", "pytest", "-q", "-p", "no:cacheprovider", TESTS_FILENAME,
            ]  # fmt: skip
            started = time.monotonic()
            try:
                completed = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=self._timeout_s,
                    check=False,
                )
            except FileNotFoundError as exc:
                raise SandboxError("the docker CLI was not found on PATH") from exc
            except subprocess.TimeoutExpired as exc:
                self._remove(container)
                partial = exc.stdout.decode() if isinstance(exc.stdout, bytes) else exc.stdout
                return build_result(
                    exit_code=None,
                    output=partial or "",
                    timed_out=True,
                    duration_s=time.monotonic() - started,
                )
            if completed.returncode == 125:  # docker itself failed (bad image, daemon down)
                raise SandboxError(f"docker could not start the container: {completed.stderr.strip()}")
            return build_result(
                exit_code=completed.returncode,
                output=completed.stdout + completed.stderr,
                timed_out=False,
                duration_s=time.monotonic() - started,
            )

    def _remove(self, container: str) -> None:
        """Best-effort cleanup: killing the CLI on timeout does not stop the container."""
        subprocess.run(
            [self._docker, "rm", "-f", container], capture_output=True, check=False, timeout=15
        )
