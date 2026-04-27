from __future__ import annotations

import json
from pathlib import Path

from keen_eyes.adapters.base import EvidenceAdapter
from keen_eyes.models import GateStatus, NormalizedEvidence


class CycloneDxAdapter(EvidenceAdapter):
    formats = {"cyclonedx", "cyclonedx-json", "sbom"}

    def parse(self, artifact_path: Path, source: str, category: str) -> list[NormalizedEvidence]:
        data = json.loads(artifact_path.read_text(encoding="utf-8"))
        components = data.get("components", [])
        vulnerabilities = data.get("vulnerabilities", [])
        evidence = [
            NormalizedEvidence(
                id=f"{source}-sbom",
                source=source,
                category=category,
                type="sbom",
                status=GateStatus.PASS,
                severity="info",
                title="CycloneDX SBOM generated",
                description=f"SBOM contains {len(components)} component(s).",
                metrics={"components": float(len(components))},
                raw_artifact=str(artifact_path),
            )
        ]
        for vuln in vulnerabilities:
            severity = str(vuln.get("ratings", [{}])[0].get("severity", "medium")).lower() if isinstance(vuln.get("ratings", []), list) else "medium"
            evidence.append(
                NormalizedEvidence(
                    id=f"{source}-{vuln.get('id', 'vulnerability')}",
                    source=source,
                    category=category,
                    type="sbom_vulnerability",
                    status=GateStatus.FAIL,
                    severity=severity,
                    title=str(vuln.get("id", "SBOM vulnerability")),
                    description=str(vuln.get("description", "")),
                    remediation="Remediate the vulnerable component or document accepted risk.",
                    raw_artifact=str(artifact_path),
                )
            )
        return evidence
