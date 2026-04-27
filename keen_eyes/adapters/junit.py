from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from keen_eyes.adapters.base import EvidenceAdapter
from keen_eyes.models import EvidenceLocation, GateStatus, NormalizedEvidence


class JUnitAdapter(EvidenceAdapter):
    formats = {"junit", "junit-xml"}

    def parse(self, artifact_path: Path, source: str, category: str) -> list[NormalizedEvidence]:
        root = ET.parse(artifact_path).getroot()
        cases = list(root.iter("testcase"))
        evidence: list[NormalizedEvidence] = []
        for index, case in enumerate(cases, start=1):
            failure = case.find("failure")
            if failure is None:
                failure = case.find("error")
            skipped = case.find("skipped")
            status = GateStatus.FAIL if failure is not None else GateStatus.SKIPPED if skipped is not None else GateStatus.PASS
            classname = case.attrib.get("classname", "")
            name = case.attrib.get("name", f"test-{index}")
            file_name = case.attrib.get("file", classname.replace(".", "/") + ".py" if classname else "")
            evidence.append(
                NormalizedEvidence(
                    id=f"{source}-{index}",
                    source=source,
                    category=category,
                    type="test_case",
                    status=status,
                    severity="high" if status == GateStatus.FAIL else "info",
                    title=f"{classname}.{name}".strip("."),
                    description=(failure.attrib.get("message", "") if failure is not None else "Test passed or was skipped."),
                    location=EvidenceLocation(file=file_name),
                    metrics={"duration_seconds": float(case.attrib.get("time", 0) or 0)},
                    raw_artifact=str(artifact_path),
                )
            )
        if not evidence:
            evidence.append(
                NormalizedEvidence(
                    id=f"{source}-summary",
                    source=source,
                    category=category,
                    type="test_suite",
                    status=GateStatus.PASS,
                    severity="info",
                    title="JUnit report parsed",
                    description="No testcase elements were present.",
                    raw_artifact=str(artifact_path),
                )
            )
        return evidence
