# API reference

Base URL when running locally: `http://127.0.0.1:8000`. Interactive documentation is served at `/docs`.

The service executes the code it receives. Keep it on localhost (see the [threat model](THREAT_MODEL.md)).

## `POST /refactor`

Runs the refactor-and-verify loop and returns the report. The call blocks until the run finishes, which can take minutes with a slow model (the UI waits up to 10 minutes).

Request body:

| Field | Type | Required | Notes |
|---|---|---|---|
| `source` | string | yes | Python module to refactor. 1 to 100,000 characters. Must parse as Python. |
| `tests` | string | yes | A pytest file. 1 to 100,000 characters. Must parse as Python. |
| `module_name` | string | no | Name the tests import the source under. Default `solution`. Must be a plain identifier that does not shadow the standard library, does not start with `test`, and is not one of `conftest`, `pytest` or a pytest dependency name. |
| `max_attempts` | integer | no | 1 to 10. Defaults to `METAMORPH_MAX_ATTEMPTS`. |
| `instructions` | string | no | Extra guidance for the model, up to 1,000 characters. |

Status codes:

| Code | Meaning |
|---|---|
| 200 | A report was produced (any verdict, including `rejected`) |
| 422 | The request body failed validation. `detail` lists the problems. |
| 429 | Too many runs are in progress (see `METAMORPH_MAX_CONCURRENT_RUNS`). Retry shortly. |
| 503 | The sandbox could not run (for example, Docker is not installed) |

Example:

```bash
curl -s http://127.0.0.1:8000/refactor \
  -H 'Content-Type: application/json' \
  -d '{
        "source": "def double(x):\n    y = x\n    y = y + x\n    return y\n",
        "tests":  "from solution import double\n\ndef test_double():\n    assert double(2) == 4\n"
      }'
```

### Report

| Field | Type | Notes |
|---|---|---|
| `id` | string | Use with `GET /runs/{id}` |
| `created_at` | string | ISO 8601, UTC |
| `provider` | string | For example `ollama:codellama` |
| `verdict` | string | `accepted`, `rejected`, `baseline_failed` or `provider_error` |
| `message` | string | One-sentence explanation |
| `baseline` | suite result | Tests run against the original source |
| `attempts` | list | One entry per model request: `number`, optional `candidate`, optional `note`, optional `suite` |
| `refactored_source` | string or null | Set only when accepted |
| `diff` | string or null | Unified diff, set only when accepted |
| `before`, `after` | metrics or null | Set only when accepted |
| `deltas` | object or null | `after - before` for each metric |
| `limitation` | string | What a passing result does and does not mean |

Suite result: `passed`, `exit_code` (null on timeout), `timed_out`, `passed_count`, `failed_count`, `duration_s`, `output` (the last 8,000 characters).

Metrics: `loc`, `sloc`, `lloc`, `comments`, `functions`, `cc_mean`, `cc_max`, `maintainability_index`.

### Verdicts

| Verdict | Meaning |
|---|---|
| `accepted` | A candidate passed the original tests, with at least one test passing |
| `rejected` | No candidate passed within the attempt limit |
| `baseline_failed` | The tests did not pass on the original source (or none were collected, or they timed out), so nothing can be verified. The model is never called. |
| `provider_error` | The model backend failed (unreachable, bad response) |

## `GET /runs/{id}`

Returns a stored report as JSON, or 404. Reports are kept in memory (the last 200) and are lost on restart.

## `GET /runs/{id}/report.md`

The same report as Markdown (`text/plain`), or 404.

## `GET /health`

```json
{"status": "ok", "version": "0.2.0", "provider": "ollama:codellama", "sandbox": "subprocess"}
```

## Evaluation CLI

```bash
cd engine
python eval/run_eval.py --cases eval/cases --out results.csv   # or: metamorph-eval
```

Uses the same `METAMORPH_*` settings. Exit codes: 0 success, 1 sandbox unavailable, 2 cases directory missing or empty. See [engine/eval/README.md](../engine/eval/README.md).
