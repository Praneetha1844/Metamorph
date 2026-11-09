# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- `METAMORPH_MAX_CONCURRENT_RUNS`: bound simultaneous runs; extra requests receive HTTP 429.
- Documentation: index, API reference, configuration reference, threat model, development guide, glossary and `SECURITY.md`.
- Container healthcheck and `.dockerignore` for the engine image; project URLs in package metadata.

### Changed
- A run now passes only when pytest exits 0 and at least one test passed, so an early process exit or an all-skipped suite no longer verifies a candidate.
- Child process output is decoded as UTF-8.
- `METAMORPH_PROVIDER=openai` without `METAMORPH_OPENAI_MODEL` is a configuration error.
- The `127.0.0.1` development origin is allowed by default.
- Module names that would shadow pytest's dependencies are rejected; empty fenced blocks in model replies are skipped.
- The evaluation CLI stops with exit code 1 when the sandbox is unavailable.

## [0.2.0]

### Added
- Python engine (`engine/`): FastAPI service and library implementing a refactor-and-verify loop.
- Pluggable model backends: Ollama, OpenAI-compatible endpoints, and a scripted fake provider.
- Sandboxed test execution: subprocess runner with timeout and POSIX resource limits, and an optional Docker runner.
- Static metrics (lines, cyclomatic complexity, maintainability index) and unified diffs via radon and difflib.
- Run reports as JSON and Markdown; `POST /refactor`, `GET /runs/{id}`, `GET /runs/{id}/report.md`, `GET /health`.
- Evaluation harness (`engine/eval`) with three hand-written sample cases. No results are published.
- UI: test input, engine client and a verified-result panel (verdict, attempts, metrics, diff).
- Architecture documentation with sequence diagram, four ADRs, `docker-compose.yml`, pre-commit config and an engine CI job.

### Changed
- README, architecture notes and roadmap rewritten to match the implemented behaviour and its limits.

## [0.1.0]

### Added
- Browser workbench: Monaco editor, sandboxed JavaScript execution in a Web Worker, remote execution through Judge0, and unverified refactor suggestions from a local Ollama model.

### Security
- Removed a hardcoded RapidAPI key from the source; the key is now read from `VITE_JUDGE0_KEY`.
- JavaScript execution moved from `eval` to a Web Worker.
