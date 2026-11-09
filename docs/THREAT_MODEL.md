# Threat model

Metamorph runs code that a user supplies and code that a language model writes. That is arbitrary code execution by design, so this page states what is and is not protected.

## Assets

- The host machine and its files, network position and credentials.
- The model API key, if one is configured.
- The integrity of a verdict: an `accepted` result should mean the supplied tests passed.

## Assumptions

- The person running the engine is the person submitting code, on their own machine.
- The tests are written or reviewed by that person.
- The API is reachable only from localhost, or only from a trusted network.

## Threats and treatment

| Threat | Subprocess sandbox (default) | Docker sandbox (opt-in) |
|---|---|---|
| Infinite loop | Timeout, then the process group is killed (POSIX) | Timeout, then the container is removed |
| Memory exhaustion | `RLIMIT_AS` cap (POSIX; not reliable on macOS; not applied on Windows) | Container memory limit |
| Large file writes | `RLIMIT_FSIZE` of 10 MB per file (POSIX) | Read-only root, 64 MB tmpfs |
| Fork bombs | Not prevented | PID limit |
| Reading the user's files | **Not prevented** | Only the workspace is mounted, read-only |
| Network access | **Not prevented** | `--network none` |
| Privilege escalation | Runs as the engine's user | `--cap-drop ALL`, `no-new-privileges` |
| Leaking the API key | The child receives only `PATH`, `HOME` (the temp directory) and a few fixed variables, not the engine's environment | Same, and no host environment |
| Heavy output | Captured in memory until the timeout; only the last 8,000 characters are kept | Same |
| Fake verification | A run passes only with exit code 0 and at least one passed test. Code that prints a fake summary is **not** detected. | Same |
| Many parallel requests | At most `METAMORPH_MAX_CONCURRENT_RUNS` runs; extra requests get 429 | Same |

## What this means in practice

- The default sandbox guards against **accidents**, not **attackers**. Do not expose the engine to untrusted users.
- Use the Docker sandbox, or run the engine in a container, when running model-written code you have not read.
- The API has no authentication or rate limiting. Bind it to `127.0.0.1`. The provided `docker-compose.yml` does.
- Passing tests is evidence, not proof. Review the diff before using an accepted refactor.

## Out of scope

Defending against a hostile test suite, side channels, kernel exploits, or a compromised model server.

## Reporting a problem

See [SECURITY.md](../SECURITY.md).
