"""Evaluation harness: run the loop over a folder of legacy snippets and write a CSV.

A case is a directory holding `source.py` and `tests.py` (the tests import the source as
`solution`). The harness records outcomes for whatever model you point it at; it ships no
results of its own.
"""

from __future__ import annotations

import argparse
import csv
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from pydantic import ValidationError

from .config import Settings
from .models import RefactorRequest
from .pipeline import run_refactor
from .providers import LLMProvider, build_provider
from .sandbox import Sandbox, SandboxError, build_sandbox

FIELDS = (
    "case",
    "provider",
    "verdict",
    "attempts",
    "baseline_passed",
    "sloc_before",
    "sloc_after",
    "cc_mean_before",
    "cc_mean_after",
    "mi_before",
    "mi_after",
    "duration_s",
)


@dataclass(frozen=True)
class Case:
    """One legacy snippet with the tests that define its behaviour."""

    name: str
    source: str
    tests: str


def load_cases(root: Path) -> list[Case]:
    """Load every `<root>/<name>/{source.py,tests.py}` pair, sorted by name."""
    if not root.is_dir():
        raise FileNotFoundError(f"cases directory not found: {root}")
    cases = [
        Case(
            name=folder.name,
            source=(folder / "source.py").read_text(encoding="utf-8"),
            tests=(folder / "tests.py").read_text(encoding="utf-8"),
        )
        for folder in sorted(p for p in root.iterdir() if p.is_dir())
        if (folder / "source.py").is_file() and (folder / "tests.py").is_file()
    ]
    if not cases:
        raise FileNotFoundError(f"no cases (folders with source.py and tests.py) in {root}")
    return cases


def evaluate(
    cases: list[Case], provider: LLMProvider, sandbox: Sandbox, *, max_attempts: int = 3
) -> list[dict[str, object]]:
    """Run each case and return one flat row per case."""
    rows: list[dict[str, object]] = []
    for case in cases:
        row: dict[str, object] = dict.fromkeys(FIELDS, "")
        row.update(case=case.name, provider=provider.name)
        started = time.monotonic()
        try:
            request = RefactorRequest(source=case.source, tests=case.tests)
        except ValidationError:
            row["verdict"] = "invalid_case"
            rows.append(row)
            continue
        report = run_refactor(request, provider, sandbox, max_attempts=max_attempts)
        row.update(
            verdict=report.verdict.value,
            attempts=len(report.attempts),
            baseline_passed=report.baseline.passed,
            duration_s=round(time.monotonic() - started, 2),
        )
        if report.before and report.after:
            row.update(
                sloc_before=report.before.sloc,
                sloc_after=report.after.sloc,
                cc_mean_before=report.before.cc_mean,
                cc_mean_after=report.after.cc_mean,
                mi_before=report.before.maintainability_index,
                mi_after=report.after.maintainability_index,
            )
        rows.append(row)
    return rows


def write_csv(rows: list[dict[str, object]], out: Path) -> None:
    """Write `rows` to `out` with a header."""
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point (`metamorph-eval`). Uses the same METAMORPH_* settings as the API."""
    parser = argparse.ArgumentParser(description="Run the refactor-and-verify loop over a folder.")
    parser.add_argument("--cases", type=Path, default=Path("eval/cases"))
    parser.add_argument("--out", type=Path, default=Path("results.csv"))
    parser.add_argument("--max-attempts", type=int, default=None)
    args = parser.parse_args(argv)

    settings = Settings.from_env()
    try:
        cases = load_cases(args.cases)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    try:
        rows = evaluate(
            cases,
            build_provider(settings),
            build_sandbox(settings),
            max_attempts=args.max_attempts or settings.max_attempts,
        )
    except SandboxError as exc:  # a broken sandbox would fail every case, so stop early
        print(f"error: sandbox unavailable: {exc}", file=sys.stderr)
        return 1
    write_csv(rows, args.out)
    print(f"wrote {len(rows)} row(s) to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
