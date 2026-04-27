# Threat Model

## Assets

- source code and tests
- evidence bundles
- scanner outputs
- audit traces
- task specifications
- secrets and credentials that must never enter reports

## Adversaries

- malicious contributor attempting to weaken gates
- compromised dependency
- model-generated insecure code
- accidental leakage of secrets into logs or evidence
- reviewer relying on unsupported compliance claims

## Key Controls

- deterministic gates for tests and scanners
- secret scanning before evidence publication
- dependency vulnerability checks
- explicit human-review-required flags
- immutable run manifests where deployed with append-only storage
- minimal provider interface for AI coding agents

