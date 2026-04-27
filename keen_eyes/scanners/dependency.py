from __future__ import annotations

from pathlib import Path

from keen_eyes.models import Finding, GateStatus, ValidationResult


class DependencyScanner:
    KNOWN_BAD = {"django==1.2", "flask==0.5", "pyyaml==3.10", "requests==2.19.0"}

    def scan(self, project_path: Path, out_dir: Path) -> ValidationResult:
        dependency_files = [p for name in ("requirements.txt", "pyproject.toml") for p in [project_path / name] if p.exists()]
        findings: list[Finding] = []
        for dep_file in dependency_files:
            text = dep_file.read_text(encoding="utf-8", errors="ignore").lower()
            for bad in self.KNOWN_BAD:
                if bad in text:
                    findings.append(
                        Finding(
                            id=f"DEP-{len(findings) + 1}",
                            title="Known vulnerable dependency pin",
                            severity="high",
                            status=GateStatus.FAIL,
                            detail=f"{bad} found in {dep_file.name}",
                            remediation="Upgrade to a supported version and regenerate lock files.",
                            control_objectives=["SI.L2-3.14.1[a]"],
                        )
                    )
        artifact = out_dir / "dependency-scan.txt"
        artifact.write_text("\n".join(f.detail for f in findings) or "No known bad dependency pins detected.", encoding="utf-8")
        return ValidationResult(
            id="dependency-scan",
            name="Dependency vulnerability scan",
            category="security",
            status=GateStatus.FAIL if findings else GateStatus.PASS,
            summary=f"{len(findings)} vulnerable dependency pins found",
            artifacts=[str(artifact)],
            findings=findings,
            control_objectives=["SI.L2-3.14.1[a]"],
        )

