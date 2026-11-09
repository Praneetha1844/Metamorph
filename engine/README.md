# metamorph-engine

Python backend for [Metamorph](../README.md). Given Python source and a test suite, it asks an LLM
for a refactor and **accepts the result only if the original tests still pass**.

```bash
pip install -e ".[dev]"
make check          # ruff, mypy, pytest
make run            # http://127.0.0.1:8000  (docs at /docs)
```

Configuration is read from `METAMORPH_*` environment variables; see [.env.example](.env.example).
Design and limits: [../docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) and [../docs/adr](../docs/adr).

The service executes the code it is given. Keep it bound to `127.0.0.1` unless it runs inside a
container with the Docker sandbox enabled.
