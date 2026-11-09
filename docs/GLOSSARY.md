# Glossary

| Term | Meaning |
|---|---|
| **Baseline** | The supplied tests run against the original source before any model call. It must pass. |
| **Candidate** | Code returned by the model that has not yet been accepted. |
| **Attempt** | One model request and what happened to its answer: no code, a syntax error, unchanged code, failed tests or passed tests. |
| **Verdict** | The outcome of a run: `accepted`, `rejected`, `baseline_failed` or `provider_error`. |
| **Verification** | Running the original, unmodified tests against a candidate. It shows the supplied tests still pass, not that behaviour is preserved. |
| **Provider** | A model backend behind the `LLMProvider` interface (Ollama, an OpenAI-compatible endpoint, or the scripted fake). |
| **Sandbox** | The component that runs the tests: a subprocess with limits, or a Docker container. |
| **Suite result** | Exit code, pass and fail counts, duration and output tail of one test run. |
| **Cyclomatic complexity (CC)** | Number of independent paths through a function, measured with radon. Lower is simpler. |
| **Maintainability index (MI)** | radon's 0 to 100 score combining size and complexity. A heuristic. |
| **Delta** | A metric after the refactor minus the metric before. Negative size or complexity is usually an improvement. |
| **Evaluation harness** | `engine/eval`: runs the loop over a folder of cases and writes a CSV. |
| **Case** | A folder with `source.py` and `tests.py` (the tests import the source as `solution`). |
