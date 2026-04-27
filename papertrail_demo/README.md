# PaperTrail Demo

PaperTrail Demo is a local-only, intentionally insecure document workflow app for testing defensive analysis tools such as Keen Eyes.

It is a safe training benchmark, not a deployable product.

## Safety Boundary

- Runs on `127.0.0.1` by default.
- Uses synthetic demo data only.
- Has no email delivery, payment processing, cloud integrations, or production accounts.
- Contains intentionally seeded application security weaknesses and compliance evidence gaps.
- Must not be exposed to a network or used with real documents, real users, real credentials, or regulated data.

## Architecture Summary

- Backend: Python + FastAPI
- UI: server-rendered Jinja templates
- Storage: SQLite
- Tests: pytest + FastAPI TestClient
- Data: synthetic users and documents seeded from `sample_data/seed.json`

## File Tree

```text
papertrail_demo/
  app/
    main.py
    database.py
    models.py
    auth.py
    audit.py
    templates/
    static/
  tests/
  docs/
    compliance-notes.md
    security-answer-key.md
  sample_data/
    seed.json
  README.md
  requirements.txt
  docker-compose.yml
```

## Local Setup

```powershell
cd papertrail_demo
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m app.database --reset
uvicorn app.main:app --host 127.0.0.1 --port 8001
```

Open [http://127.0.0.1:8001](http://127.0.0.1:8001).

## Synthetic Demo Accounts

| Username | Password | Role |
| --- | --- | --- |
| employee | employee123 | employee |
| reviewer | reviewer123 | reviewer |
| admin | admin123 | admin |

These are deliberately weak demo credentials for local training only.

## Tests

```powershell
cd papertrail_demo
pytest
```

The tests cover happy-path workflow behavior. They are intentionally not a complete security test suite.

## Docker Compose

```powershell
cd papertrail_demo
docker compose up --build
```

The Compose service binds to `127.0.0.1:8001`.

