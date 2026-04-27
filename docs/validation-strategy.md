# Validation Strategy

Keen Eyes validates every meaningful change across four dimensions:

- functionality: unit, integration, contract, end-to-end, and regression tests
- optimality: latency, throughput, memory, CPU, query count, and cost budgets where applicable
- security: static checks, secret scanning, dependency checks, negative security tests
- compliance evidence support: evidence metadata, control mapping, POA&M and SSP deltas

The MVP implements deterministic local validators and can call external OSS scanners when installed.

