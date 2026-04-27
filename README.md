# Keen Eyes

Keen Eyes is an AI-assisted software development and verification platform for disciplined Test Driven Development. It treats AI-generated code as untrusted until deterministic gates pass across four dimensions:

- desired functionality
- optimality and performance
- security
- compliance evidence support for NIST SP 800-171 Rev. 3 and NIST SP 800-171A Rev. 3

Keen Eyes does not certify compliance. It generates evidence, maps artifacts to objectives, flags human-review-required items, and packages assessor-friendly run outputs.

## MVP Quick Start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
python -m unittest discover -s tests
keen-eyes run --task tasks/sample-feature.md --project examples/secure_document_workflow --out runs/sample
```

The run writes:

- `runs/sample/run-summary.md`
- `runs/sample/evidence-manifest.json`
- `runs/sample/control-coverage.json`
- `runs/sample/poam.json`
- `runs/sample/ssp-delta.md`
- `runs/sample/validation-report.md`

## Architecture

Keen Eyes is CLI-first and self-hostable. The core Python package is organized around:

- Orchestrator: coordinates planning, agent execution, validation, compliance mapping, and report generation.
- Requirements/Test Planner: parses task specs and derives acceptance criteria, test plans, performance budgets, security invariants, and control tags.
- Coding Agent Interface: provider-pluggable interface with a deterministic local demo agent for the MVP.
- Validation Engine: runs tests, benchmarks, security checks, secret scans, dependency checks, and normalizes results.
- Compliance Evidence Engine: maps findings and artifacts to control objectives and evidence categories.
- Report Generator: writes Markdown and JSON outputs for developers and reviewers.
- Policy Layer: YAML rules for gates, control mappings, interview-required objectives, and organization-defined parameters.
- Project Profiles: `.keen-eyes.yaml` command contracts that let the same engine run Python, Node.js, Go, Rust, Java, .NET, container, IaC, and custom projects.

See [docs/architecture.md](docs/architecture.md) for deeper design notes.
See [docs/project-profiles.md](docs/project-profiles.md) for the universal project adapter format.

## Compliance Boundary

Keen Eyes supports evidence generation and objective mapping. It never marks NIST SP 800-171 compliance as complete based only on automation. Objectives can be:

- `automated_pass`
- `automated_fail`
- `partially_satisfied`
- `human_review_required`
- `not_applicable`

Final control assessment requires authorized human review. See [docs/compliance-boundary.md](docs/compliance-boundary.md).

## Demo Project

`examples/secure_document_workflow` is a dependency-light reference application with:

- role-based login
- document upload/download authorization checks
- approval workflow
- audit logging
- admin view
- validation and secure defaults
- unit/integration/security/performance tests

## Local Security Tooling

Keen Eyes can use OSS scanners when installed:

- Semgrep
- Gitleaks
- Trivy
- Checkov
- Syft / Grype
- OSV-Scanner
- OWASP ZAP
- k6

For a clean MVP environment, it also includes deterministic built-in fallback checks for tests, secret patterns, dependency metadata, and insecure-code patterns.

## Development

```powershell
python -m unittest discover -s tests
keen-eyes plan --task tasks/sample-feature.md
keen-eyes run --task tasks/sample-feature.md --project examples/secure_document_workflow --out runs/dev
```

Agent rules live in [AGENTS.md](AGENTS.md).
