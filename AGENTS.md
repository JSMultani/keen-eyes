# AGENTS.md

This repository is operated under strict TDD, security, and compliance-evidence rules.

## Required Engineering Behavior

- Follow red -> green -> refactor for meaningful feature changes.
- Generate or update failing tests before implementation.
- Do not bypass, delete, weaken, or skip tests to make a change pass.
- Do not remove security checks, scanner gates, or policy rules to make builds pass.
- Prefer minimal, reviewable diffs.
- Keep interfaces typed and testable.
- Maintain docs when architecture, behavior, security posture, or evidence behavior changes.
- Keep secrets out of source, logs, test fixtures, reports, and evidence bundles.
- Fail closed for security-sensitive defaults.

## Compliance Evidence Rules

- Do not claim NIST SP 800-171 compliance automatically.
- Do not mark controls or objectives as satisfied without concrete evidence.
- Distinguish automated evidence from human-required evidence.
- Use explicit `human_review_required` status for interview-based objectives and judgment calls.
- Update evidence manifests when checks run.
- Update POA&M artifacts when checks fail or gaps remain.
- Map artifacts to control objectives where the mapping is defensible.
- Use `not_applicable` only when the rationale is documented.

## AI Coding Rules

- Treat AI-generated code as untrusted until deterministic gates pass.
- Keep generated changes small enough for review.
- Preserve audit traceability from requirement to tests, implementation, validation, and evidence.
- Do not create fake passes, mocked compliance claims, or hard-coded happy paths.
- Do not hide failures in report generation.

## Security Rules

- Run relevant static, dependency, secret, and negative security checks for meaningful changes.
- Redact tokens, passwords, keys, session IDs, and CUI-like sample values in logs.
- Do not introduce insecure defaults.
- Do not loosen authorization checks without an explicit reviewed requirement.

## Review Rules

- Findings should include affected requirement, evidence artifact, severity, remediation, and reviewer action.
- Manual risk acceptance requires explicit human approval outside automation.

