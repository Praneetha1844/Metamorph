"""Bounded in-memory run store."""

from __future__ import annotations

import pytest

from metamorph_engine.models import RunReport, SuiteResult, Verdict
from metamorph_engine.store import RunStore


def report(run_id: str) -> RunReport:
    return RunReport(
        id=run_id,
        provider="fake",
        verdict=Verdict.REJECTED,
        message="m",
        baseline=SuiteResult(passed=True, exit_code=0),
    )


def test_evicts_oldest_beyond_capacity() -> None:
    store = RunStore(capacity=2)
    for run_id in ("a", "b", "c"):
        store.add(report(run_id))
    assert store.get("a") is None
    assert store.get("b") is not None
    assert store.get("c") is not None
    assert len(store) == 2


def test_capacity_must_be_positive() -> None:
    with pytest.raises(ValueError):
        RunStore(capacity=0)
