"""Static code metrics (radon) and unified diffs."""

from __future__ import annotations

import difflib
from statistics import fmean

from radon.complexity import cc_visit
from radon.metrics import mi_visit
from radon.raw import analyze
from radon.visitors import Function

from .models import Metrics

DELTA_FIELDS = (
    "loc",
    "sloc",
    "lloc",
    "comments",
    "functions",
    "cc_mean",
    "cc_max",
    "maintainability_index",
)


def compute_metrics(source: str) -> Metrics:
    """Compute size, cyclomatic complexity and maintainability index for `source`.

    Complexity is measured per function or method. Raises `SyntaxError` for invalid Python.
    """
    raw = analyze(source)
    complexities = [block.complexity for block in cc_visit(source) if isinstance(block, Function)]
    return Metrics(
        loc=raw.loc,
        sloc=raw.sloc,
        lloc=raw.lloc,
        comments=raw.comments,
        functions=len(complexities),
        cc_mean=round(fmean(complexities), 2) if complexities else 0.0,
        cc_max=max(complexities, default=0),
        maintainability_index=round(float(mi_visit(source, multi=True)), 2),
    )


def compute_deltas(before: Metrics, after: Metrics) -> dict[str, float]:
    """Return `after - before` for every metric. Negative complexity or size is an improvement."""
    return {
        name: round(float(getattr(after, name)) - float(getattr(before, name)), 2)
        for name in DELTA_FIELDS
    }


def unified_diff(before: str, after: str) -> str:
    """Return a unified diff between the original and refactored source."""
    return "".join(
        difflib.unified_diff(
            before.splitlines(keepends=True),
            after.splitlines(keepends=True),
            fromfile="original.py",
            tofile="refactored.py",
        )
    )
