# Architecture

Keen Eyes is a local-first validation platform with clear seams for hosted execution.

## Components

1. Orchestrator
   Coordinates a run from task intake through planning, agent execution, validation, evidence mapping, and reports.

2. Requirements/Test Planner
   Parses Markdown task specs into functional requirements, non-functional requirements, security invariants, performance budgets, control tags, and acceptance criteria.

3. Coding Agent Interface
   Encapsulates code-generation providers. The MVP ships with `DeterministicDemoAgent`, which records TDD trace entries and validates that expected demo tests exist before implementation is considered complete.

4. Validation Engine
   Runs functional tests, integration tests, performance benchmarks, security tests, secret scans, dependency checks, and optional external OSS scanner commands when available.

5. Compliance Evidence Engine
   Converts validation results into evidence objects and maps them to control objectives. Interview and judgment-based objectives are always labeled `human_review_required`.

6. Report Generator
   Writes Markdown and JSON artifacts for developers, reviewers, and assessors.

7. Policy Layer
   Stores thresholds, gates, objective mappings, interview requirements, and organization-defined parameters in version-controlled YAML.

8. Project Profile Layer
   Loads `.keen-eyes.yaml` or infers commands for common ecosystems so Keen Eyes can run as a universal harness across Python, Node.js, Go, Rust, Java, .NET, container, IaC, and custom projects.

## Proposed Repo Tree

```text
keen_eyes/
  api/
  orchestrator/
  agents/
  validators/
  scanners/
  compliance/
  reports/
  models/
  storage/
  cli/
controls/
evidence/
examples/secure_document_workflow/
tests/
docs/
```

## Milestones

- Phase 1: scaffold, architecture docs, AGENTS.md, core models, CLI, basic API, simple orchestration.
- Phase 2: task parsing, acceptance criteria, TDD trace, agent interface, run state.
- Phase 3: validation engine for tests, benchmark, security, secret, dependency checks.
- Phase 4: control mapping, evidence manifest, SSP delta, POA&M.
- Phase 5: secure document workflow demo and sample reports.
- Phase 6: hardening, seed cases, usability docs, CI.

## Stack Rationale

Python is used for orchestration because it has broad scanner/test integration support and is inexpensive to run. The MVP avoids mandatory runtime dependencies so it works on a clean developer machine. FastAPI is optional for API deployment.

See [project-profiles.md](project-profiles.md) for the adapter contract that makes Keen Eyes work across many project types.
