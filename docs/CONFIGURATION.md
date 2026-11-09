# Configuration reference

The engine reads `METAMORPH_*` environment variables at startup. Invalid values stop startup with a `ConfigError` that names the variable. A template is in [engine/.env.example](../engine/.env.example).

| Variable | Default | Valid values | Notes |
|---|---|---|---|
| `METAMORPH_PROVIDER` | `ollama` | `ollama`, `openai` | `openai` means any OpenAI-compatible chat endpoint |
| `METAMORPH_OLLAMA_URL` | `http://localhost:11434` | URL | Trailing slash removed |
| `METAMORPH_OLLAMA_MODEL` | `codellama` | model name | |
| `METAMORPH_OPENAI_BASE_URL` | `https://api.openai.com/v1` | URL | `/chat/completions` is appended |
| `METAMORPH_OPENAI_API_KEY` | empty | string | Sent only as a bearer header. Never commit it. |
| `METAMORPH_OPENAI_MODEL` | empty | model name | **Required** when the provider is `openai` |
| `METAMORPH_MAX_ATTEMPTS` | `3` | integer, at least 1 | Per-request `max_attempts` (1 to 10) overrides it |
| `METAMORPH_TEST_TIMEOUT_S` | `10` | integer, at least 1 | Seconds for one test run. The Docker sandbox adds 10 seconds for container start-up. |
| `METAMORPH_MEMORY_MB` | `512` | integer, at least 64 | Address-space cap (POSIX subprocess sandbox) or container memory (Docker sandbox) |
| `METAMORPH_MAX_CONCURRENT_RUNS` | `2` | integer, at least 1 | Extra `POST /refactor` calls get HTTP 429 |
| `METAMORPH_SANDBOX` | `subprocess` | `subprocess`, `docker` | See the [threat model](THREAT_MODEL.md) |
| `METAMORPH_DOCKER_IMAGE` | `metamorph-sandbox:latest` | image name | Built from `engine/docker/sandbox.Dockerfile` |
| `METAMORPH_CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | comma-separated origins | Browser origins allowed to call the API |

Model timeouts are fixed at 120 seconds per request in the adapters.

## UI variables (Vite)

| Variable | Default | Notes |
|---|---|---|
| `VITE_ENGINE_URL` | `http://127.0.0.1:8000` | Where the UI sends `POST /refactor` |
| `VITE_JUDGE0_KEY`, `VITE_JUDGE0_URL` | unset | Optional remote execution for non-Python languages |
| `VITE_OLLAMA_URL`, `VITE_OLLAMA_MODEL` | `http://localhost:11434`, `codellama` | The unverified "Suggest refactor" feature |

`VITE_*` values are bundled into the browser build. Do not put a production secret in them.
