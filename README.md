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

## Run Keen Eyes On Your Own Project

Keen Eyes can validate any local project that has a task file and a project profile.

1. Create a task file that describes the change or evaluation target:

```markdown
# APP-001 Validate My Project

## Functional Requirements

- Users can complete the main workflow.
- Important business rules are covered by tests.

## Non-Functional Requirements

- Key routes or jobs meet the configured performance budget.

## Security Invariants

- Unauthorized users cannot access protected data.
- Secrets must not appear in source code or logs.
- User-controlled input is validated or safely encoded.

## Performance Budgets

- list_documents_p95_ms: 100

## Compliance Tags

- AC.L1-3.1.1
- AU.L2-3.3.1
- SI.L2-3.14.1
- CM.L2-3.4.1
```

2. Add a `.keen-eyes.yaml` file to the project you want to test:

```yaml
project_type: custom
commands:
  test: "python -m pytest"
  security_test: "python -m pytest tests/security"
  benchmark: "python -m pytest tests/performance"
scanners:
  semgrep: "semgrep scan --config auto"
  osv: "osv-scanner ."
```

3. Run Keen Eyes from this repository:

```powershell
keen-eyes run --task tasks/my-project.md --project C:\path\to\my-project --out runs/my-project
```

If your project does not have a `.keen-eyes.yaml`, Keen Eyes tries to infer defaults for Python, Node.js, Go, Rust, Java, .NET, container, and custom projects. Explicit profiles are recommended for repeatable results.

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

The repository also includes `examples/universal_evidence_project`, a tiny fixture project that generates JUnit, SARIF, k6, OSV, and CycloneDX artifacts so you can test the normalized evidence pipeline end to end.

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
