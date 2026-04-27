from __future__ import annotations

import json
from pathlib import Path

from keen_eyes.adapters.base import EvidenceAdapter
from keen_eyes.models import EvidenceLocation, GateStatus, NormalizedEvidence


class SarifAdapter(EvidenceAdapter):
    formats = {"sarif", "sarif-json"}

    def parse(self, artifact_path: Path, source: str, category: str) -> list[NormalizedEvidence]:
        data = json.loads(artifact_path.read_text(encoding="utf-8"))
        evidence: list[NormalizedEvidence] = []
        for run in data.get("runs", []):
            rules = {
                rule.get("id", ""): rule
                for rule in run.get("tool", {}).get("driver", {}).get("rules", [])
            }
            for index, result in enumerate(run.get("results", []), start=len(evidence) + 1):
                rule_id = result.get("ruleId", "sarif-result")
                rule = rules.get(rule_id, {})
                level = result.get("level", "warning")
                status = GateStatus.FAIL if level in {"error", "warning"} else GateStatus.WARNING
                location = _location(result)
                evidence.append(
                    NormalizedEvidence(
                        id=f"{source}-{index}",
                        source=source,
                        category=category,
                        type="static_analysis",
                        status=status,
                        severity=_severity(level),
                        title=rule.get("name") or rule_id,
                        description=result.get("message", {}).get("text", ""),
                        remediation=rule.get("help", {}).get("text", ""),
                        location=location,
                        raw_artifact=str(artifact_path),
                    )
                )
        return evidence


def _location(result: dict[str, object]) -> EvidenceLocation:
    locations = result.get("locations", [])
    if not isinstance(locations, list) or not locations:
        return EvidenceLocation()
    physical = locations[0].get("physicalLocation", {}) if isinstance(locations[0], dict) else {}
    region = physical.get("region", {}) if isinstance(physical, dict) else {}
    artifact = physical.get("artifactLocation", {}) if isinstance(physical, dict) else {}
    return EvidenceLocation(
        file=str(artifact.get("uri", "")) if isinstance(artifact, dict) else "",
        line=int(region.get("startLine")) if isinstance(region, dict) and region.get("startLine") else None,
        column=int(region.get("startColumn")) if isinstance(region, dict) and region.get("startColumn") else None,
    )


def _severity(level: str) -> str:
    if level == "error":
        return "high"
    if level == "warning":
        return "medium"
    return "low"

