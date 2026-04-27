from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from keen_eyes.agents.demo_agent import DeterministicDemoAgent
from keen_eyes.compliance.engine import ComplianceEvidenceEngine
from keen_eyes.models import RunReport
from keen_eyes.orchestrator.planner import RequirementsPlanner
from keen_eyes.project_profile import ProjectProfile
from keen_eyes.reports.generator import ReportGenerator
from keen_eyes.storage.filesystem import FileEvidenceStore
from keen_eyes.validators.engine import ValidationEngine


class Orchestrator:
    def __init__(self) -> None:
        self.planner = RequirementsPlanner()
        self.agent = DeterministicDemoAgent()
        self.validator = ValidationEngine()
        self.compliance = ComplianceEvidenceEngine()

    def run(self, task_path: Path, project_path: Path, out_dir: Path, run_id: str = "local-run") -> RunReport:
        out_dir.mkdir(parents=True, exist_ok=True)
        plan = self.planner.plan(task_path)
        if not plan.ready:
            raise ValueError("Task is under-specified: " + "; ".join(plan.under_specified_reasons))

        profile = ProjectProfile.load(project_path)
        (out_dir / "project-profile.json").write_text(json.dumps(asdict(profile), indent=2), encoding="utf-8")
        trace = self.agent.execute(plan, project_path, out_dir, profile)
        validations = self.validator.run_all(project_path, plan, out_dir, profile)
        store = FileEvidenceStore(out_dir)
        manifest = self.compliance.generate_manifest(run_id, plan.task, validations, store)
        report = RunReport(run_id, plan.task, plan, trace, validations, manifest)
        ReportGenerator(out_dir).write_all(report)
        (out_dir / "tdd-trace.json").write_text(json.dumps(trace, indent=2), encoding="utf-8")
        return report
