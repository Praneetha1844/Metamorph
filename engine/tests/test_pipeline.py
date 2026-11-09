"""End-to-end behaviour of the refactor-and-verify loop (scripted model, real test runs)."""

from __future__ import annotations

import pytest

from metamorph_engine.models import RefactorRequest, RunReport, Verdict
from metamorph_engine.pipeline import run_refactor
from metamorph_engine.providers import FakeProvider
from metamorph_engine.report import to_markdown
from metamorph_engine.sandbox import SubprocessSandbox

LEGACY = """\
def grade(score):
    if score >= 90:
        return "A"
    else:
        if score >= 80:
            return "B"
        else:
            if score >= 70:
                return "C"
            else:
                return "F"
"""

TESTS = """\
from solution import grade

def test_grades():
    assert grade(95) == "A"
    assert grade(85) == "B"
    assert grade(75) == "C"
    assert grade(10) == "F"
"""

GOOD = """\
def grade(score):
    for floor, letter in ((90, "A"), (80, "B"), (70, "C")):
        if score >= floor:
            return letter
    return "F"
"""

BROKEN = """\
def grade(score):
    return "A"
"""


def fenced(code: str) -> str:
    return f"Here you go:\n```python\n{code}```\n"


@pytest.fixture
def sandbox() -> SubprocessSandbox:
    return SubprocessSandbox(timeout_s=30)


def request(**overrides: object) -> RefactorRequest:
    data: dict[str, object] = {"source": LEGACY, "tests": TESTS}
    data.update(overrides)
    return RefactorRequest.model_validate(data)


def test_accepts_a_refactor_that_passes_the_original_tests(sandbox: SubprocessSandbox) -> None:
    report = run_refactor(request(), FakeProvider([fenced(GOOD)]), sandbox)
    assert report.verdict is Verdict.ACCEPTED
    assert report.refactored_source == GOOD
    assert len(report.attempts) == 1
    assert report.attempts[0].verified
    assert report.diff and "+++ refactored.py" in report.diff
    assert report.deltas is not None
    assert report.deltas["cc_max"] < 0  # complexity went down


def test_rejects_when_no_candidate_passes(sandbox: SubprocessSandbox) -> None:
    provider = FakeProvider([fenced(BROKEN), fenced(BROKEN)])
    report = run_refactor(request(max_attempts=2), provider, sandbox)
    assert report.verdict is Verdict.REJECTED
    assert len(report.attempts) == 2
    assert report.refactored_source is None
    assert all(not a.verified for a in report.attempts)


def test_retries_with_failure_output_then_accepts(sandbox: SubprocessSandbox) -> None:
    provider = FakeProvider([fenced(BROKEN), fenced(GOOD)])
    report = run_refactor(request(), provider, sandbox)
    assert report.verdict is Verdict.ACCEPTED
    assert [a.verified for a in report.attempts] == [False, True]
    assert "failed the original tests" in provider.prompts[1]
    assert "assert" in provider.prompts[1]  # the pytest output is fed back


def test_baseline_failure_stops_before_calling_the_model(sandbox: SubprocessSandbox) -> None:
    provider = FakeProvider([fenced(GOOD)])
    report = run_refactor(request(source=BROKEN), provider, sandbox)
    assert report.verdict is Verdict.BASELINE_FAILED
    assert provider.prompts == []


def test_timeout_in_baseline_is_reported() -> None:
    hang = "import time\nfrom solution import grade\n\ndef test_slow():\n    time.sleep(30)\n"
    report = run_refactor(
        request(tests=hang), FakeProvider([]), SubprocessSandbox(timeout_s=1)
    )
    assert report.verdict is Verdict.BASELINE_FAILED
    assert report.baseline.timed_out


def test_candidate_that_hangs_counts_as_failed() -> None:
    hanging = "import time\n\ndef grade(score):\n    time.sleep(30)\n"
    sandbox = SubprocessSandbox(timeout_s=3)
    report = run_refactor(request(max_attempts=1), FakeProvider([fenced(hanging)]), sandbox)
    assert report.verdict is Verdict.REJECTED
    suite = report.attempts[0].suite
    assert suite is not None and suite.timed_out


def test_unusable_answers_are_recorded_not_fatal(sandbox: SubprocessSandbox) -> None:
    provider = FakeProvider(["I cannot help with that.", fenced("def grade(:\n"), fenced(LEGACY)])
    report = run_refactor(request(), provider, sandbox)
    assert report.verdict is Verdict.REJECTED
    notes = [a.note for a in report.attempts]
    assert "no valid Python" in (notes[0] or "")
    assert "syntax error" in (notes[1] or "")
    assert "identical" in (notes[2] or "")


def test_provider_failure_is_reported(sandbox: SubprocessSandbox) -> None:
    report = run_refactor(request(), FakeProvider([]), sandbox)
    assert report.verdict is Verdict.PROVIDER_ERROR
    assert report.attempts[0].note and "provider error" in report.attempts[0].note


def test_markdown_report_contains_verdict_metrics_and_limitation(
    sandbox: SubprocessSandbox,
) -> None:
    report = run_refactor(request(), FakeProvider([fenced(GOOD)]), sandbox)
    text = to_markdown(report)
    assert "**Verdict:** accepted" in text
    assert "Mean cyclomatic complexity" in text
    assert "```diff" in text
    assert "do not prove" in text


def test_report_round_trips_through_json(sandbox: SubprocessSandbox) -> None:
    report = run_refactor(request(), FakeProvider([fenced(GOOD)]), sandbox)
    assert RunReport.model_validate_json(report.model_dump_json()) == report


@pytest.mark.parametrize(
    "overrides",
    [
        {"source": "def broken(:\n"},
        {"tests": ""},
        {"module_name": "os"},
        {"module_name": "test_solution"},
        {"module_name": "not an identifier"},
        {"max_attempts": 0},
    ],
)
def test_invalid_requests_are_rejected(overrides: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        request(**overrides)
