from __future__ import annotations

import json
from pathlib import Path

from keen_eyes.adapters.base import EvidenceAdapter
from keen_eyes.models import GateStatus, NormalizedEvidence


class OsvAdapter(EvidenceAdapter):
    formats = {"osv", "osv-json"}

    def parse(self, artifact_path: Path, source: str, category: str) -> list[NormalizedEvidence]:
        data = json.loads(artifact_path.read_text(encoding="utf-8"))
        evidence: list[NormalizedEvidence] = []
        results = data.get("results", [])
        for result_index, result in enumerate(results, start=1):
            packages = result.get("packages", []) if isinstance(result, dict) else []
            for package in packages:
                package_info = package.get("package", {}) if isinstance(package, dict) else {}
                for vuln in package.get("vulnerabilities", []):
                    vuln_id = vuln.get("id", f"osv-{result_index}")
                    evidence.append(
                        NormalizedEvidence(
                            id=f"{source}-{vuln_id}",
                            source=source,
                            category=category,
                            type="dependency_vulnerability",
                            status=GateStatus.FAIL,
                            severity="high",
                            title=f"{package_info.get('name', 'dependency')} {vuln_id}",
                            description=vuln.get("summary", ""),
                            remediation="Upgrade or replace the affected dependency and regenerate dependency evidence.",
                            raw_artifact=str(artifact_path),
                        )
                    )
        if not evidence:
            evidence.append(
                NormalizedEvidence(
                    id=f"{source}-clean",
                    source=source,
                    category=category,
                    type="dependency_vulnerability_scan",
                    status=GateStatus.PASS,
                    severity="info",
                    title="No OSV vulnerabilities reported",
                    description="OSV report did not contain vulnerabilities.",
                    raw_artifact=str(artifact_path),
                )
            )
        return evidence

