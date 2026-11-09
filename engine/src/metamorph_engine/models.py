"""Typed request, result and report models shared by the pipeline and the REST API."""

from __future__ import annotations

import ast
import keyword
import sys
from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator

MAX_CODE_CHARS = 100_000
# Names that would shadow pytest or its dependencies when the module sits next to the tests.
RESERVED_MODULE_NAMES = frozenset(
    {"test_suite", "conftest", "pytest", "_pytest", "pluggy", "iniconfig", "packaging", "py"}
)

LIMITATION_NOTE = (
    "Accepted means the supplied tests still pass. Passing tests do not prove the refactor "
    "preserves behaviour that the tests do not cover."
)


class Verdict(StrEnum):
    """Final outcome of a refactor run."""

    ACCEPTED = "accepted"
    REJECTED = "rejected"
    BASELINE_FAILED = "baseline_failed"
    PROVIDER_ERROR = "provider_error"


def _require_python(value: str, label: str) -> str:
    try:
        ast.parse(value)
    except SyntaxError as exc:
        raise ValueError(f"{label} is not valid Python: {exc.msg} (line {exc.lineno})") from exc
    return value


class RefactorRequest(BaseModel):
    """Source under refactor plus the test suite that defines its behaviour."""

    source: str = Field(min_length=1, max_length=MAX_CODE_CHARS)
    tests: str = Field(min_length=1, max_length=MAX_CODE_CHARS)
    module_name: str = Field(
        default="solution",
        description="Name the tests import the source under, e.g. `from solution import calc`.",
    )
    max_attempts: int | None = Field(default=None, ge=1, le=10)
    instructions: str | None = Field(default=None, max_length=1000)

    @field_validator("source")
    @classmethod
    def _source_is_python(cls, value: str) -> str:
        return _require_python(value, "source")

    @field_validator("tests")
    @classmethod
    def _tests_are_python(cls, value: str) -> str:
        return _require_python(value, "tests")

    @field_validator("module_name")
    @classmethod
    def _module_name_is_safe(cls, value: str) -> str:
        if (
            not value.isidentifier()
            or keyword.iskeyword(value)
            or value in sys.stdlib_module_names
            or value in RESERVED_MODULE_NAMES
            or value.startswith("test")
        ):
            raise ValueError(
                "module_name must be a plain identifier that does not shadow the standard "
                "library or start with 'test'"
            )
        return value


class SuiteResult(BaseModel):
    """Outcome of running the test suite once."""

    passed: bool
    exit_code: int | None
    timed_out: bool = False
    passed_count: int = 0
    failed_count: int = 0
    duration_s: float = 0.0
    output: str = ""


class Metrics(BaseModel):
    """Static metrics for one version of the code (computed with radon)."""

    loc: int
    sloc: int
    lloc: int
    comments: int
    functions: int
    cc_mean: float
    cc_max: int
    maintainability_index: float


class Attempt(BaseModel):
    """One request to the model and what happened to its answer."""

    number: int
    candidate: str | None = None
    note: str | None = None
    suite: SuiteResult | None = None

    @property
    def verified(self) -> bool:
        return self.suite is not None and self.suite.passed


class RunReport(BaseModel):
    """Structured result of one refactor-and-verify run."""

    id: str = Field(default_factory=lambda: uuid4().hex)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    provider: str
    verdict: Verdict
    message: str
    baseline: SuiteResult
    attempts: list[Attempt] = Field(default_factory=list)
    refactored_source: str | None = None
    diff: str | None = None
    before: Metrics | None = None
    after: Metrics | None = None
    deltas: dict[str, float] | None = None
    limitation: str = LIMITATION_NOTE
