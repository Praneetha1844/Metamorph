# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

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
