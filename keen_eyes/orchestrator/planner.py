from __future__ import annotations

import re
from pathlib import Path

from keen_eyes.models import RequirementPlan, TaskSpec


class RequirementsPlanner:
    """Parses structured Markdown tasks into a deterministic execution plan."""

    REQUIRED_SECTIONS = {
        "Functional Requirements": "functional_requirements",
        "Non-Functional Requirements": "non_functional_requirements",
        "Security Invariants": "security_invariants",
        "Performance Budgets": "performance_budgets",
        "Compliance Tags": "compliance_tags",
    }

    def parse_task(self, path: Path) -> TaskSpec:
        text = path.read_text(encoding="utf-8")
        title_match = re.search(r"^#\s+(.+)$", text, flags=re.MULTILINE)
        title = title_match.group(1).strip() if title_match else path.stem
        task_id = title.split()[0] if title else path.stem
        sections = self._sections(text)
        budgets: dict[str, float] = {}
        for line in sections.get("Performance Budgets", []):
            if ":" in line:
                key, value = line.split(":", 1)
                budgets[key.strip()] = float(re.sub(r"[^0-9.]", "", value) or 0)
        return TaskSpec(
            task_id=task_id,
            title=title,
            functional_requirements=sections.get("Functional Requirements", []),
            non_functional_requirements=sections.get("Non-Functional Requirements", []),
            security_invariants=sections.get("Security Invariants", []),
            performance_budgets=budgets,
            compliance_tags=sections.get("Compliance Tags", []),
            source_path=str(path),
        )

    def plan(self, task_path: Path) -> RequirementPlan:
        task = self.parse_task(task_path)
        reasons: list[str] = []
        if len(task.functional_requirements) < 1:
            reasons.append("At least one functional requirement is required.")
        if len(task.security_invariants) < 1:
            reasons.append("At least one security invariant is required.")
        if len(task.performance_budgets) < 1:
            reasons.append("At least one measurable performance budget is required.")
        if len(task.compliance_tags) < 1:
            reasons.append("At least one compliance/control tag is required.")

        acceptance = [f"AC-{i + 1}: {req}" for i, req in enumerate(task.functional_requirements)]
        test_plan = [
            "Create failing unit tests for role, document, authorization, and audit behavior.",
            "Create integration tests for upload, approval, download, and admin audit workflows.",
            "Create negative security tests for unauthorized download, unsafe filename, and log redaction.",
            "Create benchmark enforcing configured p95 latency budget.",
        ]
        evidence_plan = [
            "Collect test outputs and normalized validation results.",
            "Collect security, secret, and dependency scan outputs.",
            "Map evidence to selected NIST SP 800-171 Rev. 3 objectives.",
            "Generate SSP delta, POA&M, manifest, and validation report.",
        ]
        return RequirementPlan(task, acceptance, test_plan, evidence_plan, reasons)

    def _sections(self, text: str) -> dict[str, list[str]]:
        current: str | None = None
        sections: dict[str, list[str]] = {}
        for raw in text.splitlines():
            heading = re.match(r"^##\s+(.+)$", raw)
            if heading:
                current = heading.group(1).strip()
                sections.setdefault(current, [])
                continue
            if current and raw.strip().startswith("- "):
                sections[current].append(raw.strip()[2:].strip())
        return sections

