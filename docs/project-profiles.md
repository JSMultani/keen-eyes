# Project Profiles

Keen Eyes is intended to be a universal validation harness. The core engine stays the same, while each project declares how to test, security-test, benchmark, and scan itself through a `.keen-eyes.yaml` file.

If no profile exists, Keen Eyes tries to infer defaults for common ecosystems.

## Profile Schema

```yaml
project_type: python-fastapi
commands:
  test: "python -m pytest"
  security_test: "python -m pytest tests/security"
  benchmark: "python -m pytest tests/performance"
scanners:
  semgrep: "semgrep scan --config auto"
  osv: "osv-scanner ."
artifacts:
  - name: unit-tests
    path: reports/junit.xml
    format: junit
    category: functional
    controls: "AC.L1-3.1.1[a]"
  - name: semgrep
    path: reports/semgrep.sarif
    format: sarif
    category: security
    controls: "CM.L2-3.4.1[a]"
```

All commands run locally from the project root. Commands under `scanners` are optional. Each scanner command becomes its own normalized validation result and evidence artifact.

Artifacts are optional but recommended. Declared artifacts are parsed by adapters, converted into normalized evidence JSON under `runs/<name>/normalized/`, and then included in the validation report, evidence manifest, and POA&M flow.

## Built-In Artifact Formats

- `junit` or `junit-xml`: unit, integration, and end-to-end test reports
- `sarif` or `sarif-json`: SAST, IaC, and scanner findings
- `k6` or `k6-json`: performance summaries
- `osv` or `osv-json`: dependency vulnerability results
- `cyclonedx`, `cyclonedx-json`, or `sbom`: SBOM evidence and SBOM vulnerability records

## Supported Patterns

Keen Eyes can run on any project that can expose local commands. Built-in inference covers:

- Python: `pytest` or `unittest`
- Node.js: `npm test`, `npm run test:security`, `npm run benchmark`
- Go: `go test ./...`
- Rust: `cargo test`
- Java Maven: `mvn test`
- Java Gradle: `./gradlew test`
- .NET: `dotnet test`
- Docker/IaC/custom projects: profile-driven commands

## Examples

### Node.js

```yaml
project_type: node
commands:
  test: "npm test"
  security_test: "npm run test:security"
  benchmark: "npm run benchmark"
scanners:
  dependency: "osv-scanner ."
```

### Go

```yaml
project_type: go
commands:
  test: "go test ./..."
  security_test: "go test ./... -run Security"
  benchmark: "go test ./... -bench ."
```

### Custom

```yaml
project_type: custom
commands:
  test: "./scripts/test.sh"
  security_test: "./scripts/security-test.sh"
  benchmark: "./scripts/benchmark.sh"
```

## Universal Rule

Keen Eyes does not need to understand every framework internally. It needs a repeatable command contract and normalized evidence output. Project profiles provide that contract.
