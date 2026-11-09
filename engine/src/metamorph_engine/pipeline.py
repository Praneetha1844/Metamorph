"""The refactor-and-verify loop.

1. Run the supplied tests against the original source (baseline). If they do not pass, there is
   nothing to verify a refactor against, so stop.
2. Ask the model for a refactor. Reject syntactically invalid or unchanged answers.
3. Run the ORIGINAL tests against the candidate. Accept only if they all pass.
4. Otherwise retry with the failure output, up to `max_attempts`.
"""

from __future__ import annotations

import ast

from .metrics import compute_deltas, compute_metrics, unified_diff
from .models import Attempt, RefactorRequest, RunReport, SuiteResult, Verdict
from .prompts import SYSTEM_PROMPT, build_prompt, extract_code
from .providers import LLMError, LLMProvider
from .sandbox import Sandbox

FEEDBACK_LIMIT = 3000


def _baseline_message(baseline: SuiteResult) -> str:
    if baseline.timed_out:
        return "The tests timed out on the original source, so a refactor cannot be verified."
    return (
        "The tests do not pass on the original source (or no tests were collected), "
        "so a refactor cannot be verified."
    )


def run_refactor(
    request: RefactorRequest,
    provider: LLMProvider,
    sandbox: Sandbox,
    *,
    max_attempts: int = 3,
) -> RunReport:
    """Run the loop and return a structured report. Sandbox failures propagate to the caller."""
    limit = request.max_attempts or max_attempts
    baseline = sandbox.run_tests(request.source, request.tests, request.module_name)
    if not baseline.passed:
        return RunReport(
            provider=provider.name,
            verdict=Verdict.BASELINE_FAILED,
            message=_baseline_message(baseline),
            baseline=baseline,
        )

    attempts: list[Attempt] = []
    previous: str | None = None
    failure: str | None = None

    for number in range(1, limit + 1):
        prompt = build_prompt(
            request.source,
            instructions=request.instructions,
            previous_candidate=previous,
            failure_output=failure,
        )
        try:
            reply = provider.complete(prompt, system=SYSTEM_PROMPT)
        except LLMError as exc:
            attempts.append(Attempt(number=number, note=f"provider error: {exc}"))
            return RunReport(
                provider=provider.name,
                verdict=Verdict.PROVIDER_ERROR,
                message=f"The model backend failed on attempt {number}: {exc}",
                baseline=baseline,
                attempts=attempts,
            )

        candidate = extract_code(reply)
        if candidate is None:
            attempts.append(Attempt(number=number, note="reply contained no valid Python code"))
            previous, failure = reply[:FEEDBACK_LIMIT], "The reply had no ```python block."
            continue
        try:
            ast.parse(candidate)
        except SyntaxError as exc:
            attempts.append(
                Attempt(number=number, candidate=candidate, note=f"syntax error: {exc.msg}")
            )
            previous, failure = candidate, f"SyntaxError: {exc.msg} (line {exc.lineno})"
            continue
        if candidate.strip() == request.source.strip():
            attempts.append(
                Attempt(number=number, candidate=candidate, note="candidate identical to source")
            )
            previous, failure = candidate, "The code was returned unchanged. Make a real refactor."
            continue

        suite = sandbox.run_tests(candidate, request.tests, request.module_name)
        attempts.append(Attempt(number=number, candidate=candidate, suite=suite))
        if suite.passed:
            before = compute_metrics(request.source)
            after = compute_metrics(candidate)
            return RunReport(
                provider=provider.name,
                verdict=Verdict.ACCEPTED,
                message=f"Accepted on attempt {number}: the original tests pass on the refactor.",
                baseline=baseline,
                attempts=attempts,
                refactored_source=candidate,
                diff=unified_diff(request.source, candidate),
                before=before,
                after=after,
                deltas=compute_deltas(before, after),
            )
        previous = candidate
        failure = "Tests timed out." if suite.timed_out else suite.output[-FEEDBACK_LIMIT:]

    return RunReport(
        provider=provider.name,
        verdict=Verdict.REJECTED,
        message=f"No candidate passed the original tests in {limit} attempt(s).",
        baseline=baseline,
        attempts=attempts,
    )
