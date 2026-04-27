from __future__ import annotations

import json
from pathlib import Path

from keen_eyes.adapters.base import EvidenceAdapter
from keen_eyes.models import GateStatus, NormalizedEvidence


class K6Adapter(EvidenceAdapter):
    formats = {"k6", "k6-json"}

    def parse(self, artifact_path: Path, source: str, category: str) -> list[NormalizedEvidence]:
        data = json.loads(artifact_path.read_text(encoding="utf-8"))
        evidence: list[NormalizedEvidence] = []
        metrics = data.get("metrics", {})
        checks = data.get("root_group", {}).get("checks", [])
        duration = metrics.get("http_req_duration", {}) if isinstance(metrics, dict) else {}
        values = duration.get("values", {}) if isinstance(duration, dict) else {}
        p95 = float(values.get("p(95)", values.get("p95", 0)) or 0)
        thresholds = duration.get("thresholds", {}) if isinstance(duration, dict) else {}
        failed_thresholds = [name for name, item in thresholds.items() if isinstance(item, dict) and item.get("ok") is False]
        evidence.append(
            NormalizedEvidence(
                id=f"{source}-http_req_duration",
                source=source,
                category=category,
                type="performance_metric",
                status=GateStatus.FAIL if failed_thresholds else GateStatus.PASS,
                severity="medium" if failed_thresholds else "info",
                title="HTTP request duration",
                description="k6 HTTP duration thresholds evaluated.",
                metrics={"p95_ms": p95},
                raw_artifact=str(artifact_path),
            )
        )
        for index, check in enumerate(checks, start=1):
            passes = int(check.get("passes", 0) or 0)
            fails = int(check.get("fails", 0) or 0)
            evidence.append(
                NormalizedEvidence(
                    id=f"{source}-check-{index}",
                    source=source,
                    category=category,
                    type="runtime_check",
                    status=GateStatus.FAIL if fails else GateStatus.PASS,
                    severity="medium" if fails else "info",
                    title=str(check.get("name", f"check-{index}")),
                    description=f"k6 check passes={passes} fails={fails}.",
                    metrics={"passes": passes, "fails": fails},
                    raw_artifact=str(artifact_path),
                )
            )
        return evidence

