# Developer Guide

## Local Checks

```powershell
python -m unittest discover -s tests
python -m keen_eyes.cli.main run --task tasks/sample-feature.md --project examples/secure_document_workflow --out runs/dev
```

## Adding Validators

Implement a validator that returns `ValidationResult` objects, then register it in `ValidationEngine`.

## Adding Controls

Update `controls/control-map.yaml`, add evidence rules in `controls/evidence-rules.yaml`, and add interview requirements in `controls/interview-required.yaml`.

