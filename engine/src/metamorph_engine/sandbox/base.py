"""Sandbox interface and helpers shared by the runners."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Protocol

from ..models import SuiteResult

TESTS_FILENAME = "test_suite.py"
OUTPUT_LIMIT_CHARS = 8000

_COUNT = re.compile(r"(\d+) (passed|failed|errors?)")


class SandboxError(RuntimeError):
    """The sandbox itself could not run (missing Docker, unwritable temp dir, ...)."""


class Sandbox(Protocol):
    """Runs a test suite against a module and reports the outcome."""

    name: str

    def run_tests(self, source: str, tests: str, module_name: str) -> SuiteResult:
        """Run `tests` against `source` saved as `<module_name>.py`."""
        ...


def write_workspace(root: Path, source: str, tests: str, module_name: str) -> None:
    """Write the module and the test file into `root`."""
    (root / f"{module_name}.py").write_text(source, encoding="utf-8")
    (root / TESTS_FILENAME).write_text(tests, encoding="utf-8")


def tail(text: str, limit: int = OUTPUT_LIMIT_CHARS) -> str:
    """Keep the end of `text`: pytest prints failures last, so the tail is what matters."""
    return text if len(text) <= limit else "...[truncated]...\n" + text[-limit:]


def build_result(
    *, exit_code: int | None, output: str, timed_out: bool, duration_s: float
) -> SuiteResult:
    """Turn raw process results into a `SuiteResult`.

    A run passes only on exit code 0 **and** at least one test reported as passed. pytest exits 5
    when no tests were collected, and a module that ends the process early (for example with
    `os._exit(0)` at import time) exits 0 without running anything. Both are treated as failures
    so an empty or short-circuited run can never verify a refactor. This guards against
    accidents; code that deliberately prints a fake summary is outside what it can detect.
    """
    passed_count = failed_count = 0
    for number, label in _COUNT.findall(output):
        if label == "passed":
            passed_count = int(number)
        else:
            failed_count += int(number)
    return SuiteResult(
        passed=exit_code == 0 and not timed_out and passed_count > 0,
        exit_code=exit_code,
        timed_out=timed_out,
        passed_count=passed_count,
        failed_count=failed_count,
        duration_s=round(duration_s, 3),
        output=tail(output),
    )
