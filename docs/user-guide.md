# User Guide

## Plan a Task

```powershell
keen-eyes plan --task tasks/sample-feature.md
```

## Run End-to-End Validation

```powershell
keen-eyes run --task tasks/sample-feature.md --project examples/secure_document_workflow --out runs/sample
```

For any other project, add a `.keen-eyes.yaml` file to the target project root or let Keen Eyes infer common defaults. See `docs/project-profiles.md`.

## Read Results

Start with `validation-report.md`, then inspect `evidence-manifest.json`, `control-coverage.json`, and `poam.json`.
