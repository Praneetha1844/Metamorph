"""Render a `RunReport` as Markdown. The JSON form is the model itself (`model_dump_json`)."""

from __future__ import annotations

from .metrics import DELTA_FIELDS
from .models import RunReport

_LABELS = {
    "loc": "Lines",
    "sloc": "Source lines",
    "lloc": "Logical lines",
    "comments": "Comment lines",
    "functions": "Functions",
    "cc_mean": "Mean cyclomatic complexity",
    "cc_max": "Max cyclomatic complexity",
    "maintainability_index": "Maintainability index",
}


def to_markdown(report: RunReport) -> str:
    """Return a human-readable report."""
    lines = [
        f"# Refactor report `{report.id}`",
        "",
        f"- **Verdict:** {report.verdict.value}",
        f"- **Provider:** {report.provider}",
        f"- **Summary:** {report.message}",
        f"- **Baseline tests:** {'pass' if report.baseline.passed else 'fail'} "
        f"({report.baseline.passed_count} passed, {report.baseline.failed_count} failed)",
        "",
        "## Attempts",
        "",
    ]
    if report.attempts:
        lines += ["| # | Outcome |", "|---|---|"]
        for attempt in report.attempts:
            if attempt.suite is not None:
                outcome = "tests passed" if attempt.suite.passed else (
                    "tests timed out" if attempt.suite.timed_out else "tests failed"
                )
            else:
                outcome = attempt.note or "no result"
            lines.append(f"| {attempt.number} | {outcome} |")
    else:
        lines.append("No attempts were made.")

    if report.before and report.after and report.deltas is not None:
        lines += ["", "## Static metrics", "", "| Metric | Before | After | Change |", "|---|---|---|---|"]
        for name in DELTA_FIELDS:
            lines.append(
                f"| {_LABELS[name]} | {getattr(report.before, name)} | "
                f"{getattr(report.after, name)} | {report.deltas[name]:+g} |"
            )
    if report.diff:
        lines += ["", "## Diff", "", "```diff", report.diff.rstrip("\n"), "```"]
    lines += ["", f"> {report.limitation}", ""]
    return "\n".join(lines)
