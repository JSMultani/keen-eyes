from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from keen_eyes.models import GateStatus, ObjectiveStatus, RunReport


class ReportGenerator:
    def __init__(self, out_dir: Path) -> None:
        self.out_dir = out_dir

    def write_all(self, report: RunReport) -> None:
        self.write_json("evidence-manifest.json", report.evidence_manifest.to_dict())
        self.write_json("control-coverage.json", [asdict(result) for result in report.evidence_manifest.control_results])
        self.write_json("poam.json", self._poam(report))
        self.write_markdown("run-summary.md", self._summary(report))
        self.write_markdown("ssp-delta.md", self._ssp_delta(report))
        self.write_markdown("validation-report.md", self._validation_report(report))

    def write_json(self, name: str, payload: object) -> None:
        (self.out_dir / name).write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def write_markdown(self, name: str, text: str) -> None:
        (self.out_dir / name).write_text(text, encoding="utf-8")

    def _summary(self, report: RunReport) -> str:
        status = "PASS" if report.passed else "FAIL"
        lines = [
            f"# Keen Eyes Run Summary: {status}",
            "",
            f"- Run ID: `{report.run_id}`",
            f"- Task: `{report.task.task_id}` {report.task.title}",
            f"- Source: `{report.task.source_path}`",
            "",
            "## Gates",
        ]
        for result in report.validations:
            lines.append(f"- {result.name}: `{result.status.value}` - {result.summary}")
        lines += ["", "## Human Review Required"]
        for control in report.evidence_manifest.control_results:
            if control.status == ObjectiveStatus.HUMAN_REVIEW_REQUIRED:
                lines.append(f"- {control.objective_id}: {control.rationale}")
        return "\n".join(lines) + "\n"

    def _validation_report(self, report: RunReport) -> str:
        lines = ["# Validation Report", "", "## Acceptance Criteria"]
        lines.extend(f"- {criterion}" for criterion in report.plan.acceptance_criteria)
        lines.extend(["", "## TDD Trace"])
        lines.extend(f"- {entry['phase']}: {entry['detail']}" for entry in report.tdd_trace)
        lines.extend(["", "## Findings"])
        findings = [finding for result in report.validations for finding in result.findings]
        if not findings:
            lines.append("- No failed findings from automated checks.")
        for finding in findings:
            lines.append(f"- {finding.id} `{finding.severity}` {finding.title}: {finding.detail} Remediation: {finding.remediation}")
        lines.extend(["", "## Normalized Evidence"])
        normalized_results = [result for result in report.validations if result.normalized_evidence or result.id.startswith("artifact-")]
        if not normalized_results:
            lines.append("- No declared artifacts were normalized in this run.")
        for result in normalized_results:
            passed = sum(1 for item in result.normalized_evidence if item.status.value == "pass")
            failed = sum(1 for item in result.normalized_evidence if item.status.value == "fail")
            warnings = sum(1 for item in result.normalized_evidence if item.status.value == "warning")
            lines.append(f"- {result.name}: {len(result.normalized_evidence)} record(s), pass={passed}, fail={failed}, warning={warnings}")
        lines.extend(["", "## Compliance Boundary"])
        lines.append("Keen Eyes generated supporting evidence only. Final NIST SP 800-171 assessment requires human judgment.")
        return "\n".join(lines) + "\n"

    def _ssp_delta(self, report: RunReport) -> str:
        lines = [
            "# SSP Delta",
            "",
            f"Task `{report.task.task_id}` generated evidence for: {', '.join(report.task.compliance_tags)}.",
            "",
            "## Automated Evidence Added",
        ]
        for artifact in report.evidence_manifest.artifacts:
            lines.append(f"- {artifact.id}: {artifact.summary}")
        lines.extend(["", "## Human Review Notes"])
        for control in report.evidence_manifest.control_results:
            if control.status == ObjectiveStatus.HUMAN_REVIEW_REQUIRED:
                lines.append(f"- {control.objective_id}: interview/manual examination required.")
        return "\n".join(lines) + "\n"

    def _poam(self, report: RunReport) -> dict[str, object]:
        items = []
        for result in report.validations:
            if result.status == GateStatus.FAIL:
                for finding in result.findings or []:
                    items.append(
                        {
                            "id": finding.id,
                            "title": finding.title,
                            "severity": finding.severity,
                            "source_validation": result.id,
                            "controls": finding.control_objectives,
                            "remediation": finding.remediation,
                            "status": "open",
                        }
                    )
        for control in report.evidence_manifest.control_results:
            if control.status in {ObjectiveStatus.HUMAN_REVIEW_REQUIRED, ObjectiveStatus.PARTIALLY_SATISFIED}:
                items.append(
                    {
                        "id": f"POAM-{control.objective_id}",
                        "title": f"Evidence gap for {control.objective_id}",
                        "severity": "medium",
                        "source_validation": "compliance-evidence",
                        "controls": [control.objective_id],
                        "remediation": control.rationale,
                        "status": "human_review_required",
                    }
                )
        return {"run_id": report.run_id, "items": items}
