"""REST API behaviour with an injected scripted provider."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from metamorph_engine.api import create_app
from metamorph_engine.config import Settings
from metamorph_engine.models import SuiteResult
from metamorph_engine.providers import FakeProvider
from metamorph_engine.sandbox import SandboxError, SubprocessSandbox
from metamorph_engine.store import RunStore

SOURCE = "def double(x):\n    y = x\n    y = y + x\n    return y\n"
TESTS = "from solution import double\n\ndef test_double():\n    assert double(2) == 4\n"
REFACTORED = "```python\ndef double(x):\n    return 2 * x\n```"


def make_client(replies: list[str]) -> TestClient:
    app = create_app(Settings(), FakeProvider(replies), SubprocessSandbox(timeout_s=30))
    return TestClient(app)


def test_health_reports_configuration() -> None:
    body = make_client([]).get("/health").json()
    assert body["status"] == "ok"
    assert body["provider"] == "fake"
    assert body["sandbox"] == "subprocess"


def test_refactor_then_fetch_the_stored_run() -> None:
    client = make_client([REFACTORED])
    response = client.post("/refactor", json={"source": SOURCE, "tests": TESTS})
    assert response.status_code == 200
    report = response.json()
    assert report["verdict"] == "accepted"
    assert report["refactored_source"] == "def double(x):\n    return 2 * x\n"

    fetched = client.get(f"/runs/{report['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == report["id"]

    markdown = client.get(f"/runs/{report['id']}/report.md")
    assert markdown.status_code == 200
    assert "**Verdict:** accepted" in markdown.text


def test_unknown_run_is_404() -> None:
    client = make_client([])
    assert client.get("/runs/nope").status_code == 404
    assert client.get("/runs/nope/report.md").status_code == 404


def test_invalid_request_is_422() -> None:
    client = make_client([])
    assert client.post("/refactor", json={"source": "def (:", "tests": TESTS}).status_code == 422
    assert client.post("/refactor", json={"source": SOURCE}).status_code == 422


def test_sandbox_failure_is_503() -> None:
    class Broken:
        name = "broken"

        def run_tests(self, source: str, tests: str, module_name: str) -> SuiteResult:
            raise SandboxError("no docker")

    client = TestClient(create_app(Settings(), FakeProvider([]), Broken()))
    response = client.post("/refactor", json={"source": SOURCE, "tests": TESTS})
    assert response.status_code == 503


def test_store_evicts_oldest_beyond_capacity() -> None:
    client = make_client([REFACTORED, REFACTORED])
    store = RunStore(capacity=1)
    first = client.post("/refactor", json={"source": SOURCE, "tests": TESTS}).json()
    from metamorph_engine.models import RunReport

    store.add(RunReport.model_validate(first))
    second = RunReport.model_validate(first).model_copy(update={"id": "second"})
    store.add(second)
    assert store.get(first["id"]) is None
    assert store.get("second") is not None
    with pytest.raises(ValueError):
        RunStore(capacity=0)
