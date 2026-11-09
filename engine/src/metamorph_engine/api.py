"""REST API.

    POST /refactor            run the loop, return the report (429 when too many runs are active)
    GET  /runs/{id}           fetch a stored report (JSON)
    GET  /runs/{id}/report.md fetch it as Markdown
    GET  /health              liveness and configuration summary

The service executes the code it receives. Bind it to localhost, or run it in a container with
the Docker sandbox, and never expose it to untrusted users.
"""

from __future__ import annotations

from threading import BoundedSemaphore

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from . import __version__
from .config import Settings
from .models import RefactorRequest, RunReport
from .pipeline import run_refactor
from .providers import LLMProvider, build_provider
from .report import to_markdown
from .sandbox import Sandbox, SandboxError, build_sandbox
from .store import RunStore


def create_app(
    settings: Settings | None = None,
    provider: LLMProvider | None = None,
    sandbox: Sandbox | None = None,
) -> FastAPI:
    """Build the application. `provider` and `sandbox` can be injected (tests do this)."""
    cfg = settings or Settings.from_env()
    llm = provider or build_provider(cfg)
    box = sandbox or build_sandbox(cfg)
    store = RunStore()
    # Each run starts a test process and a model call; bound them so a burst of requests
    # cannot exhaust the host. Excess requests get HTTP 429 and can be retried.
    slots = BoundedSemaphore(cfg.max_concurrent_runs)

    app = FastAPI(title="Metamorph engine", version=__version__)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(cfg.cors_origins),
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {
            "status": "ok",
            "version": __version__,
            "provider": llm.name,
            "sandbox": box.name,
        }

    # Sync endpoint on purpose: FastAPI runs it in a worker thread, so the blocking
    # model call and test run do not stall the event loop.
    @app.post("/refactor", response_model=RunReport)
    def refactor(request: RefactorRequest) -> RunReport:
        if not slots.acquire(blocking=False):
            raise HTTPException(status_code=429, detail="too many runs in progress, retry shortly")
        try:
            report = run_refactor(request, llm, box, max_attempts=cfg.max_attempts)
        except SandboxError as exc:
            raise HTTPException(status_code=503, detail=f"sandbox unavailable: {exc}") from exc
        finally:
            slots.release()
        store.add(report)
        return report

    @app.get("/runs/{run_id}", response_model=RunReport)
    def get_run(run_id: str) -> RunReport:
        report = store.get(run_id)
        if report is None:
            raise HTTPException(status_code=404, detail="run not found")
        return report

    @app.get("/runs/{run_id}/report.md", response_class=PlainTextResponse)
    def get_run_markdown(run_id: str) -> str:
        report = store.get(run_id)
        if report is None:
            raise HTTPException(status_code=404, detail="run not found")
        return to_markdown(report)

    return app
