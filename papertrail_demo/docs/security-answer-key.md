# PaperTrail Demo Private Evaluator Guide

This guide lists intentionally seeded weaknesses and compliance gaps for defensive evaluation. It avoids exploit scripts, payloads, and step-by-step abuse instructions.

## Seeded Weaknesses

| ID | Category | Severity | Location | Expected Detection Method | Notes |
| --- | --- | --- | --- | --- | --- |
| PT-001 | Broken access control | High | `app/main.py` `/documents/{document_id}/download` | Code review, DAST, authorization tests | Download checks authentication but does not verify document ownership, approval state, reviewer/admin role, or least privilege. |
| PT-002 | Broken access control | High | `app/main.py` `/documents/{document_id}/decision` | Code review, API tests | Any authenticated user can change document approval status. |
| PT-003 | Broken access control | Medium | `app/main.py` `/audit` | Code review, DAST | Any authenticated user can view audit events instead of admin-only access. |
| PT-004 | Insecure authentication/session handling | High | `app/auth.py`, `app/main.py` `/login` | Code review, SAST, config review | Passwords are stored and compared as plaintext; sessions use username-only cookies without signing, expiry, `HttpOnly`, `Secure`, or `SameSite` settings. |
| PT-005 | Weak password policy | Medium | `sample_data/seed.json`, `README.md` | Config review, compliance review | Demo users have weak fixed passwords and no password policy enforcement. |
| PT-006 | Missing brute-force protection | Medium | `app/main.py` `/login` | Code review, DAST, abuse-case tests | Login has no rate limiting, lockout, or throttling. |
| PT-007 | XSS-style output handling concern | Medium | `app/templates/documents.html`, `app/templates/detail.html`, `app/templates/audit.html` | Template review, SAST, DAST | Selected user-controlled values are rendered with `safe`, bypassing normal template escaping. |
| PT-008 | Unsafe upload validation | High | `app/main.py` `/documents/upload` | Code review, SAST, file-upload tests | Upload accepts arbitrary filenames and text content, writes files by provided filename, and lacks size/type validation. |
| PT-009 | Overly permissive CORS/API exposure | Medium | `app/main.py` CORS middleware and `/api/documents` | Config review, DAST | CORS allows all origins and the unauthenticated API exposes document metadata and content. |
| PT-010 | Excessive error detail/information disclosure | Low | `app/main.py` HTTPException details and `FastAPI(debug=True)` | Config review, DAST | Error messages expose implementation details and debug mode is enabled. |
| PT-011 | Sensitive data in logs | High | `app/main.py` failed login audit event | Code review, log review, SAST | Failed login audit details include submitted password material. |
| PT-012 | Missing security headers | Medium | `app/main.py` middleware | Config review, DAST | The app lacks common hardening headers such as CSP, frame protections, nosniff, and HSTS. |
| PT-013 | Insecure defaults | Medium | `app/main.py`, `docker-compose.yml` | Config review | Debug mode is enabled and the benchmark should remain local-only. Compose binds locally, but app defaults remain intentionally weak. |
| PT-014 | Incomplete audit integrity/accountability | Medium | `app/audit.py`, `app/main.py` | Code review, compliance review | Audit logs are mutable database rows with no integrity protection, retention policy, or complete coverage. |
| PT-015 | SQL construction issue | High | `app/main.py` `/documents` search | Code review, SAST | Search query is built using string interpolation rather than parameter binding. |
| PT-016 | Supply-chain visibility gap | Medium | Repository root | Dependency/SBOM review | No SBOM, dependency lockfile, provenance record, or vulnerability-scan output is provided. |

## Seeded Compliance-Process Gaps

| ID | Category | Severity | Location | Expected Detection Method | Notes |
| --- | --- | --- | --- | --- | --- |
| PT-C-001 | SSP gap | Medium | `docs/compliance-notes.md` | Compliance evidence review | SSP-style documentation is incomplete and explicitly not authoritative. |
| PT-C-002 | POA&M gap | Medium | Repository docs | Compliance evidence review | Known weaknesses are not represented in a formal POA&M artifact. |
| PT-C-003 | Evidence manifest gap | Medium | Repository docs | Compliance evidence review | No structured evidence manifest maps tests/findings to NIST objectives. |
| PT-C-004 | Access review traceability gap | Medium | Repository docs | Compliance evidence review | No access review records or reviewer attestations exist. |
| PT-C-005 | Baseline configuration gap | Medium | Repository docs | Compliance evidence review | No baseline configuration inventory or secure configuration standard exists. |
| PT-C-006 | Incident/logging coverage gap | Medium | `app/audit.py`, docs | Compliance evidence review, code review | Audit coverage is incomplete and not mapped to incident response procedures. |

## Suggested High-Level Detection Dimensions

- Desired functionality: run happy-path tests and inspect role workflow behavior.
- Optimality/performance: add benchmark coverage for document search/listing and upload handling.
- Security: run SAST, DAST, dependency review, config review, and negative authorization tests.
- Compliance evidence support: verify SSP, POA&M, evidence manifest, access review, baseline configuration, and audit evidence coverage.

