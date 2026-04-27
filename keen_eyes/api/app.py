from __future__ import annotations

from pathlib import Path

from keen_eyes.orchestrator import Orchestrator


def create_app():
    try:
        from fastapi import FastAPI
    except ImportError as exc:
        raise RuntimeError("Install keen-eyes[api] to use the API server.") from exc

    app = FastAPI(title="Keen Eyes", version="0.1.0")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/runs")
    def run(task_path: str, project_path: str, out_dir: str = "runs/api") -> dict[str, object]:
        report = Orchestrator().run(Path(task_path), Path(project_path), Path(out_dir), run_id="api-run")
        return {"run_id": report.run_id, "passed": report.passed}

    return app

