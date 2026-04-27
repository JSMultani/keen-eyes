# SDW-001 Secure Document Workflow

## Functional Requirements

- Users can log in with predefined role-based accounts.
- Authors can upload documents with safe filenames.
- Approvers can approve submitted documents.
- Users can download only documents they are authorized to access.
- Admins can view an audit log.

## Non-Functional Requirements

- The document listing path p95 latency must be at or below 50 ms in local benchmark conditions.
- Audit events must be generated for login, upload, approval, download, and unauthorized access attempts.

## Security Invariants

- Unauthorized users must not download protected documents.
- Filenames must reject path traversal and control characters.
- Logs must not contain passwords or session tokens.
- Default accounts must use roles with least privilege.

## Performance Budgets

- list_documents_p95_ms: 50

## Compliance Tags

- AC.L1-3.1.1
- AU.L2-3.3.1
- SI.L2-3.14.1
- CM.L2-3.4.1

