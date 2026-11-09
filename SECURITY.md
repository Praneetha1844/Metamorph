# Security policy

## Reporting a vulnerability

Please report security issues privately through GitHub: open the **Security** tab of this repository and choose **Report a vulnerability** (private security advisory). Do not open a public issue for a vulnerability.

Include what you found, how to reproduce it, and the version or commit. This is a personal project maintained by one person, so there is no guaranteed response time, but reports are read.

## Scope

The engine executes code it is sent, by design. Please read the [threat model](docs/THREAT_MODEL.md) first. In scope: sandbox escapes from the Docker sandbox, ways to make a run pass without the tests passing, secrets leaking through logs or reports, and flaws in request validation. Out of scope: the default subprocess sandbox not being a security boundary (documented), and running the API on a public network.

## Secrets

No credentials belong in this repository. Model keys are read from environment variables. If you find a secret in the history, report it so it can be rotated.
