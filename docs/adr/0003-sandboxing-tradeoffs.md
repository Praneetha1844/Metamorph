# ADR 0003: Sandboxing trade-offs

Status: accepted

## Context

Verification means executing code supplied by a user and produced by a model. That is arbitrary code execution by design. The engine must be usable with no setup, and safe to harden when needed.

## Options considered

| Option | Isolation | Cost |
|---|---|---|
| In-process `exec` | None | Trivial, unacceptable: a hang or crash takes down the service |
| Child process with timeout and rlimits | Contains runaway loops, memory and file growth | No dependencies; same OS user and network |
| Docker container (no network, read-only, capped) | Strong, including network and filesystem | Needs Docker; slower start |
| Remote execution service (Judge0) | Strong | Third-party dependency, latency, key handling |

## Decision

Provide two runners behind one `Sandbox` interface.

- **`SubprocessSandbox` (default).** Runs `pytest` with the current interpreter in a throwaway directory. A small bootstrap sets `RLIMIT_AS`, `RLIMIT_CPU` and `RLIMIT_FSIZE` inside the child, then calls `pytest.main`. It does not use `preexec_fn`, which is unsafe when the parent is multi-threaded (FastAPI runs sync endpoints in a thread pool). On timeout the whole process group is killed (POSIX). The environment is reduced to `PATH` and a few fixed variables.
- **`DockerSandbox` (opt-in).** `docker run --rm --network none --read-only --cap-drop ALL --security-opt no-new-privileges` with memory, CPU and PID limits and the workspace mounted read-only. On timeout the container is removed explicitly, because killing the CLI does not stop it.

## Consequences

- The default runner guards against accidents, **not attackers**. The child shares the user, the filesystem and the network. The README and architecture notes say so, and the API is meant for localhost.
- `RLIMIT_AS` is POSIX-only and is not reliably enforced on macOS; on Windows the limits are skipped and only the timeout applies.
- Output is limited to the last 8,000 characters, because pytest prints failures last.
- A missing or broken sandbox raises `SandboxError`, surfaced as HTTP 503. It is never reported as a failed refactor.
- The Docker runner and `docker-compose.yml` are written against the CLI but have not been exercised in CI.

## Revisit when

The service is exposed beyond localhost (add authentication, make Docker mandatory, consider gVisor or Firecracker), or Windows becomes a primary platform.
