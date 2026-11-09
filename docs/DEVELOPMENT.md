# Development guide

## Requirements

- Python 3.12 or newer for the engine
- Node 20 or newer for the UI
- Optional: Ollama for a local model, Docker for the Docker sandbox

## Engine

```bash
cd engine
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
make check      # ruff, mypy (strict), pytest
make run        # http://127.0.0.1:8000
```

Several engine tests start real `pytest` child processes in temporary directories, so they need a working `python` and a writable temp directory. No test needs a network or a model: providers are replaced by `FakeProvider` or by httpx's in-memory transport.

## UI

```bash
npm install
npm run dev     # http://localhost:5173
npm run lint
npm run build
```

Point the UI at a different engine with `VITE_ENGINE_URL`.

## Layout

See the project structure in the [README](../README.md) and the module table in [ARCHITECTURE](ARCHITECTURE.md).

## Adding a model provider

1. Create `engine/src/metamorph_engine/providers/<name>.py` with a class that has a `name` attribute and `complete(prompt, *, system=None) -> str`.
2. Convert every backend failure to `LLMError`.
3. Register it in `providers/__init__.py` (`build_provider`) and add the setting to `config.py`, validating the new value.
4. Test it with `httpx.MockTransport`, as in `tests/test_providers.py`.

## Adding a sandbox

1. Implement the `Sandbox` protocol (`name`, `run_tests(source, tests, module_name) -> SuiteResult`).
2. Build the result with `sandbox.base.build_result` so the pass rule stays in one place.
3. Raise `SandboxError` only when the sandbox itself cannot run.
4. Register it in `sandbox/__init__.py`.

## Conventions

- Typed code; `ruff` and strict `mypy` must be clean.
- Commits use conventional prefixes (`feat`, `fix`, `docs`, `test`, `chore`, `ci`).
- No secrets in the repository. Configuration goes in environment variables and `.env.example`.
- Claims in the docs must match the code. Do not publish numbers that were not measured.

## Evaluation

See [engine/eval/README.md](../engine/eval/README.md). Run it against your own model; the repository ships no results.
