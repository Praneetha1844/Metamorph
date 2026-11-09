# Roadmap

## Done (v0.2.0)

- [x] Accept a test file alongside the source and run it before and after a refactor
- [x] Show a diff between original and suggested code
- [x] Reject suggestions that fail the original tests; retry with the failure output
- [x] Report simple metrics (lines, cyclomatic complexity, maintainability index) before and after
- [x] Move test execution to a server-side sandbox (subprocess runner, optional Docker runner)
- [x] Engine test suite (provider adapters, sandbox, pipeline, API, metrics, harness)

## Next

- [ ] Publish a first evaluation run (model, prompt version, number of repetitions, spread) from `engine/eval`
- [ ] Larger, less synthetic evaluation set drawn from open-source code with existing tests
- [ ] Persist run reports (SQLite) instead of keeping the last 200 in memory
- [ ] Optional mutation testing to estimate how strong the supplied tests are
- [ ] Exercise the Docker sandbox and compose file in CI
- [ ] Unit tests for the UI's `src/lib` modules

## Known gaps (found in review)

- [ ] Cap the amount of captured process output; a test that prints heavily is only limited by the timeout today
- [ ] Windows: no memory or CPU limits and no process-tree kill; use the Docker sandbox there
- [ ] Rate limiting and authentication if the API is ever reachable by anyone but the local user
- [ ] Verify refactors under more than one Python version

## Later

- [ ] Multi-file refactoring with project-level context
- [ ] JavaScript and TypeScript support behind the same pipeline
- [ ] Streaming model output to the UI
- [ ] Token and cost tracking per run
- [ ] Authentication, if the service is ever exposed beyond localhost
