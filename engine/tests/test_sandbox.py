"""Sandbox behaviour. These run real pytest child processes in temporary directories."""

from __future__ import annotations

import pytest

from metamorph_engine.config import Settings
from metamorph_engine.sandbox import SubprocessSandbox, build_sandbox
from metamorph_engine.sandbox.base import build_result, tail

SOURCE = "def add(a, b):\n    return a + b\n"
GOOD_TESTS = "from solution import add\n\ndef test_add():\n    assert add(1, 2) == 3\n"
BAD_TESTS = "from solution import add\n\ndef test_add():\n    assert add(1, 2) == 4\n"


def test_passing_suite() -> None:
    result = SubprocessSandbox(timeout_s=30).run_tests(SOURCE, GOOD_TESTS, "solution")
    assert result.passed
    assert result.exit_code == 0
    assert result.passed_count == 1
    assert result.failed_count == 0
    assert not result.timed_out


def test_failing_suite_reports_failure_output() -> None:
    result = SubprocessSandbox(timeout_s=30).run_tests(SOURCE, BAD_TESTS, "solution")
    assert not result.passed
    assert result.failed_count == 1
    assert "assert 3 == 4" in result.output


def test_timeout_kills_the_run() -> None:
    slow = "import time\n\ndef test_slow():\n    time.sleep(30)\n"
    result = SubprocessSandbox(timeout_s=1).run_tests(SOURCE, slow, "solution")
    assert result.timed_out
    assert not result.passed
    assert result.exit_code is None


def test_empty_suite_never_counts_as_passing() -> None:
    result = SubprocessSandbox(timeout_s=30).run_tests(SOURCE, "x = 1\n", "solution")
    assert not result.passed


def test_import_error_in_source_fails() -> None:
    broken = "import nonexistent_pkg_xyz\n"
    result = SubprocessSandbox(timeout_s=30).run_tests(broken, GOOD_TESTS, "solution")
    assert not result.passed


def test_invalid_limits_are_rejected() -> None:
    with pytest.raises(ValueError):
        SubprocessSandbox(timeout_s=0)
    with pytest.raises(ValueError):
        SubprocessSandbox(memory_mb=8)


def test_build_result_parses_counts_and_exit_code() -> None:
    result = build_result(
        exit_code=1, output="2 failed, 3 passed in 0.1s", timed_out=False, duration_s=0.1
    )
    assert (result.passed_count, result.failed_count, result.passed) == (3, 2, False)


def test_tail_keeps_the_end() -> None:
    text = "a" * 20 + "END"
    assert tail(text, 10).endswith("END")
    assert tail("short", 10) == "short"


def test_build_sandbox_selects_by_setting() -> None:
    assert build_sandbox(Settings()).name == "subprocess"
    assert build_sandbox(Settings(sandbox="docker")).name == "docker"
