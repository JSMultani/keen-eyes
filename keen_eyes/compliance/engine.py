from __future__ import annotations

from pathlib import Path

from keen_eyes.models import Artifact, ControlResult, EvidenceManifest, GateStatus, ObjectiveStatus, TaskSpec, ValidationResult, utc_now_iso
from keen_eyes.storage.filesystem import FileEvidenceStore


OBJECTIVE_METHODS = {
    "AC.L1-3.1.1[a]": "test",
    "AC.L1-3.1.1[b]": "interview",
    "AU.L2-3.3.1[a]": "examine",
    "AU.L2-3.3.1[b]": "test",
    "SI.L2-3.14.1[a]": "test",
    "SI.L2-3.14.1[b]": "examine",
    "CM.L2-3.4.1[a]": "examine",
}

INTERVIEW_REQUIRED = {"AC.L1-3.1.1[b]"}


class ComplianceEvidenceEngine:
    def generate_manifest(
        self,
        run_id: str,
        task: TaskSpec,
        validations: list[ValidationResult],
        store: FileEvidenceStore,
    ) -> EvidenceManifest:
        artifacts: list[Artifact] = []
        objective_evidence: dict[str, list[str]] = {}
        objective_failed: set[str] = set()

        for result in validations:
            artifact_path = result.artifacts[0] if result.artifacts else store.write_text(f"{result.id}.txt", result.summary)
            artifact = Artifact(
                id=result.id,
                type=result.category,
                path=str(Path(artifact_path)),
                status=result.status.value,
                automated=True,
                assessment_methods=[self._method_for(result)],
                control_objectives=result.control_objectives,
                summary=result.summary,
                hash_sha256=store.sha256(Path(artifact_path)),
            )
            artifacts.append(artifact)
            for objective in result.control_objectives:
                objective_evidence.setdefault(objective, []).append(result.id)
                if result.status == GateStatus.FAIL:
                    objective_failed.add(objective)

        all_objectives = sorted(set(OBJECTIVE_METHODS) | set(objective_evidence) | INTERVIEW_REQUIRED)
        control_results: list[ControlResult] = []
        for objective in all_objectives:
            method = OBJECTIVE_METHODS.get(objective, "examine")
            evidence_ids = objective_evidence.get(objective, [])
            if objective in INTERVIEW_REQUIRED:
                status = ObjectiveStatus.HUMAN_REVIEW_REQUIRED
                rationale = "Objective requires interview or human assessment evidence."
            elif objective in objective_failed:
                status = ObjectiveStatus.AUTOMATED_FAIL
                rationale = "One or more automated evidence artifacts failed."
            elif evidence_ids:
                status = ObjectiveStatus.AUTOMATED_PASS
                rationale = "Automated evidence artifacts passed for this objective."
            else:
                status = ObjectiveStatus.PARTIALLY_SATISFIED
                rationale = "No automated artifact fully covers this objective yet."
            control_results.append(ControlResult(objective, status, method, evidence_ids, rationale))

        return EvidenceManifest("0.1", run_id, utc_now_iso(), task.task_id, artifacts, control_results)

    def _method_for(self, result: ValidationResult) -> str:
        if result.id in {"unit-integration-tests", "security-tests", "performance-benchmark", "dependency-scan"}:
            return "test"
        return "examine"

