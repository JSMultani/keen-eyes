# Compliance Boundary

Keen Eyes supports compliance evidence. It does not certify compliance and does not replace assessors.

Automation can:

- collect test and scanner artifacts
- generate evidence metadata
- map artifacts to NIST SP 800-171 Rev. 3 requirements and 800-171A assessment objectives
- identify gaps and failed checks
- draft SSP deltas and POA&M entries

Automation cannot:

- prove implementation intent
- perform required interviews
- make final risk acceptance decisions
- decide organizational applicability without human approval
- certify full NIST SP 800-171 compliance

Every objective is labeled with one of:

- `automated_pass`
- `automated_fail`
- `partially_satisfied`
- `human_review_required`
- `not_applicable`

Interview objectives default to `human_review_required` unless a human review artifact is attached.

