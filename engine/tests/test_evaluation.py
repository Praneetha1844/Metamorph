"""Evaluation harness: case loading, row building and CSV output."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from metamorph_engine.evaluation import FIELDS, evaluate, load_cases, write_csv
from metamorph_engine.providers import FakeProvider
from metamorph_engine.sandbox import SubprocessSandbox

CASES = Path(__file__).resolve().parents[1] / "eval" / "cases"

WORDCOUNT = """\
```python
from collections import Counter


def wc(s):
    words = (w.strip(".,!?;:").lower() for w in s.split())
    return dict(Counter(w for w in words if w))
```
"""


def test_bundled_cases_load_sorted() -> None:
    names = [case.name for case in load_cases(CASES)]
    assert names == sorted(names)
    assert {"legacy_discount", "legacy_matrix", "legacy_wordcount"} <= set(names)


def test_missing_or_empty_directory_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_cases(tmp_path / "nope")
    with pytest.raises(FileNotFoundError):
        load_cases(tmp_path)


def test_rows_and_csv_for_one_case(tmp_path: Path) -> None:
    cases = [c for c in load_cases(CASES) if c.name == "legacy_wordcount"]
    rows = evaluate(cases, FakeProvider([WORDCOUNT]), SubprocessSandbox(timeout_s=30))
    assert len(rows) == 1
    assert rows[0]["verdict"] == "accepted"
    assert rows[0]["attempts"] == 1
    assert rows[0]["baseline_passed"] is True

    out = tmp_path / "results.csv"
    write_csv(rows, out)
    with out.open(encoding="utf-8", newline="") as handle:
        read = list(csv.DictReader(handle))
    assert list(read[0].keys()) == list(FIELDS)
    assert read[0]["case"] == "legacy_wordcount"


def test_main_stops_with_exit_code_1_when_the_sandbox_is_unavailable(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    from metamorph_engine import evaluation
    from metamorph_engine.sandbox import SandboxError

    class Broken:
        name = "broken"

        def run_tests(self, source: str, tests: str, module_name: str) -> object:
            raise SandboxError("no docker")

    monkeypatch.setattr(evaluation, "build_sandbox", lambda settings: Broken())
    monkeypatch.setattr(evaluation, "build_provider", lambda settings: FakeProvider([]))
    code = evaluation.main(["--cases", str(CASES), "--out", str(tmp_path / "out.csv")])
    assert code == 1
    assert "sandbox unavailable" in capsys.readouterr().err
