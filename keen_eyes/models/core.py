from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class GateStatus(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    SKIPPED = "skipped"


class ObjectiveStatus(StrEnum):
    AUTOMATED_PASS = "automated_pass"
    AUTOMATED_FAIL = "automated_fail"
    PARTIALLY_SATISFIED = "partially_satisfied"
    HUMAN_REVIEW_REQUIRED = "human_review_required"
    NOT_APPLICABLE = "not_applicable"


@dataclass(frozen=True)
class EvidenceLocation:
    file: str = ""
    line: int | None = None
    column: int | None = None


@dataclass(frozen=True)
class NormalizedEvidence:
    id: str
    source: str
    category: str
    type: str
    status: GateStatus
    severity: str
    title: str
    description: str
    remediation: str = ""
    location: EvidenceLocation | None = None
    metrics: dict[str, float] = field(default_factory=dict)
    raw_artifact: str = ""
    control_objectives: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class TaskSpec:
    task_id: str
    title: str
    functional_requirements: list[str]
    non_functional_requirements: list[str]
    security_invariants: list[str]
    performance_budgets: dict[str, float]
    compliance_tags: list[str]
    source_path: str


@dataclass(frozen=True)
class RequirementPlan:
    task: TaskSpec
    acceptance_criteria: list[str]
    test_plan: list[str]
    evidence_plan: list[str]
    under_specified_reasons: list[str] = field(default_factory=list)

    @property
    def ready(self) -> bool:
        return not self.under_specified_reasons


@dataclass(frozen=True)
class Finding:
    id: str
    title: str
    severity: str
    status: GateStatus
    detail: str
    remediation: str
    control_objectives: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ValidationResult:
    id: str
    name: str
    category: str
    status: GateStatus
    summary: str
    artifacts: list[str] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)
    metrics: dict[str, float] = field(default_factory=dict)
    control_objectives: list[str] = field(default_factory=list)
    normalized_evidence: list[NormalizedEvidence] = field(default_factory=list)


@dataclass(frozen=True)
class Artifact:
    id: str
    type: str
    path: str
    status: str
    automated: bool
    assessment_methods: list[str]
    control_objectives: list[str]
    summary: str
    hash_sha256: str = ""


@dataclass(frozen=True)
class ControlResult:
    objective_id: str
    status: ObjectiveStatus
    assessment_method: str
    evidence_ids: list[str]
    rationale: str


@dataclass(frozen=True)
class EvidenceManifest:
    schema_version: str
    run_id: str
    generated_at: str
    task_id: str
    artifacts: list[Artifact]
    control_results: list[ControlResult]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RunReport:
    run_id: str
    task: TaskSpec
    plan: RequirementPlan
    tdd_trace: list[dict[str, str]]
    validations: list[ValidationResult]
    evidence_manifest: EvidenceManifest

    @property
    def passed(self) -> bool:
        return all(result.status != GateStatus.FAIL for result in self.validations)


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
