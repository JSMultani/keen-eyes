# PTD-001 PaperTrail Demo Defensive Evaluation

## Functional Requirements

- Users can sign in with synthetic demo accounts.
- Employees can upload documents.
- Users can search and list documents.
- Users can open document detail pages.
- Users can download documents.
- Reviewers can approve or reject documents.
- Admins can view a dashboard with users and documents.
- Audit events appear in a simple log view.

## Non-Functional Requirements

- The document list page should respond within a reasonable local benchmark budget.
- The app must remain local-only and bind to localhost by default.
- The app must use synthetic data only.
- Defensive analysis should produce reviewer-friendly evidence artifacts.

## Security Invariants

- Unauthorized users should not access documents they are not permitted to view.
- Review decisions should require reviewer or admin role.
- Audit logs should not contain submitted passwords, tokens, or other sensitive values.
- Uploaded files should be validated for safe names, size, and expected content type.
- User-controlled content should be safely encoded in rendered pages.
- API routes should require appropriate authentication and authorization.
- CORS and debug defaults should be constrained for local training use.
- Common security headers should be reviewed.

## Performance Budgets

- list_documents_p95_ms: 100

## Compliance Tags

- AC.L1-3.1.1
- AU.L2-3.3.1
- SI.L2-3.14.1
- CM.L2-3.4.1
