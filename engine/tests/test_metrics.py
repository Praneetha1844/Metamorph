"""Static metrics and diffs."""

from __future__ import annotations

import pytest

from metamorph_engine.metrics import compute_deltas, compute_metrics, unified_diff

NESTED = """\
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

FLAT = """\
def grade(score):
    for floor, letter in ((90, "A"), (80, "B"), (70, "C")):
        if score >= floor:
            return letter
    return "F"
"""


def test_counts_functions_and_complexity() -> None:
    metrics = compute_metrics(NESTED)
    assert metrics.functions == 1
    assert metrics.cc_max == 4  # three decision points plus the base path
    assert metrics.cc_mean == 4.0


def test_module_without_functions_has_zero_complexity() -> None:
    metrics = compute_metrics("X = 1\n")
    assert metrics.functions == 0
    assert metrics.cc_mean == 0.0
    assert metrics.cc_max == 0


def test_delta_is_after_minus_before() -> None:
    before = compute_metrics(NESTED)
    after = compute_metrics(FLAT)
    deltas = compute_deltas(before, after)
    assert deltas["cc_max"] == after.cc_max - before.cc_max
    assert deltas["sloc"] == after.sloc - before.sloc
    assert deltas["sloc"] < 0  # the flat version is shorter


def test_invalid_python_raises() -> None:
    with pytest.raises(SyntaxError):
        compute_metrics("def broken(:\n")


def test_unified_diff_names_both_files_and_marks_changes() -> None:
    diff = unified_diff("a = 1\n", "a = 2\n")
    assert "--- original.py" in diff
    assert "+++ refactored.py" in diff
    assert "-a = 1" in diff
    assert "+a = 2" in diff
    assert unified_diff("same\n", "same\n") == ""
