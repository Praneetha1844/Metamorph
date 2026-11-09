"""Default sandbox: pytest in a child process with a timeout and POSIX resource limits.

This limits accidents (infinite loops, runaway memory, huge files), not attackers: the child
runs as the same OS user with the same network access. See docs/adr/0003.
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from ..models import SuiteResult
from .base import TESTS_FILENAME, SandboxError, build_result, write_workspace

# Sets limits inside the child, then runs pytest. Avoids `preexec_fn`, which is unsafe when
# the parent is multi-threaded (FastAPI runs sync endpoints in a thread pool).
_BOOTSTRAP = """
import sys
try:
    import resource
    mem, cpu = int(sys.argv[1]), int(sys.argv[2])
    resource.setrlimit(resource.RLIMIT_AS, (mem, mem))
    resource.setrlimit(resource.RLIMIT_CPU, (cpu, cpu))
    resource.setrlimit(resource.RLIMIT_FSIZE, (10485760, 10485760))
except (ImportError, ValueError, OSError):
    pass
import pytest
raise SystemExit(pytest.main(sys.argv[3:]))
"""


class SubprocessSandbox:
    """Runs the suite with the current interpreter in a throwaway directory."""

    name = "subprocess"

    def __init__(self, timeout_s: float = 10.0, memory_mb: int = 512) -> None:
        if timeout_s <= 0 or memory_mb < 64:
            raise ValueError("timeout_s must be > 0 and memory_mb >= 64")
        self._timeout_s = timeout_s
        self._memory_bytes = memory_mb * 1024 * 1024

    def run_tests(self, source: str, tests: str, module_name: str) -> SuiteResult:
        try:
            tmp = tempfile.TemporaryDirectory(prefix="metamorph-")
        except OSError as exc:
            raise SandboxError(f"could not create a workspace: {exc}") from exc
        with tmp as directory:
            root = Path(directory)
            write_workspace(root, source, tests, module_name)
            return self._run(root)

    def _run(self, root: Path) -> SuiteResult:
        cpu_seconds = int(self._timeout_s) + 1
        command = [
            sys.executable,
            "-c",
            _BOOTSTRAP,
            str(self._memory_bytes),
            str(cpu_seconds),
            "-q",
            "-p",
            "no:cacheprovider",
            "--rootdir",
            str(root),
            TESTS_FILENAME,
        ]
        env = {
            "PATH": os.environ.get("PATH", ""),
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONHASHSEED": "0",
            "HOME": str(root),
        }
        if "SYSTEMROOT" in os.environ:  # required for Python to start on Windows
            env["SYSTEMROOT"] = os.environ["SYSTEMROOT"]
        started = time.monotonic()
        try:
            process = subprocess.Popen(
                command,
                cwd=root,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                start_new_session=os.name == "posix",
            )
        except OSError as exc:
            raise SandboxError(f"could not start the test process: {exc}") from exc
        timed_out = False
        try:
            output, _ = process.communicate(timeout=self._timeout_s)
        except subprocess.TimeoutExpired:
            timed_out = True
            _kill_tree(process)
            output, _ = process.communicate()
        return build_result(
            exit_code=None if timed_out else process.returncode,
            output=output or "",
            timed_out=timed_out,
            duration_s=time.monotonic() - started,
        )


def _kill_tree(process: subprocess.Popen[str]) -> None:
    """Kill the child and, on POSIX, everything it spawned."""
    try:
        if os.name == "posix":
            os.killpg(os.getpgid(process.pid), signal.SIGKILL)
        else:
            process.kill()
    except (ProcessLookupError, PermissionError):
        pass
