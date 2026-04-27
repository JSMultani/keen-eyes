# UEP-001 Universal Evidence Pipeline Demo

## Functional Requirements

- The dummy project exposes a passing business-rule test.
- The dummy project generates declared test, security, performance, dependency, and SBOM artifacts.

## Non-Functional Requirements

- The evidence pipeline should parse all declared artifacts into normalized evidence records.
- The run should generate assessor-friendly artifacts and coverage summaries.

## Security Invariants

- Static analysis findings from SARIF must be captured as security evidence.
- Dependency scanner output must be captured as supply-chain evidence.
- SBOM output must be captured as supply-chain evidence.

## Performance Budgets

- list_documents_p95_ms: 100

## Compliance Tags

- AC.L1-3.1.1
- AU.L2-3.3.1
- SI.L2-3.14.1
- CM.L2-3.4.1
