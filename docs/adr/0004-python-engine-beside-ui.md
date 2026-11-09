# ADR 0004: A Python engine beside the browser UI

Status: accepted

## Context

The first version was a browser-only React app. Verified refactoring needs to run a test suite safely, which a browser cannot do for Python, and it would expose any execution key to the page.

## Options considered

1. **Keep everything in the browser** and call Judge0 for tests. Exposes the key, depends on a third party, and cannot return structured metrics.
2. **Node backend.** Same language as the UI, but the metrics and test tooling (radon, pytest) are Python.
3. **Python backend (FastAPI)** with the UI as a client.

## Decision

Add `engine/`, a Python 3.12 package with a FastAPI app, and keep the UI as a thin client of `POST /refactor`. The original browser features (Worker execution for JavaScript, Judge0, unverified suggestions) stay as they were.

## Consequences

- Two toolchains in one repository: Node for the UI and Python for the engine, each with its own CI job.
- The engine is also a library and a CLI (`metamorph-eval`), so it can be used without the UI.
- Verified refactoring is Python-only. Supporting another language means a new runner and metric tool, not a UI change.
- The UI talks to the engine over CORS; allowed origins are configured explicitly.
- Reports are held in memory; persistence is a roadmap item.
