from __future__ import annotations

import re
from pathlib import Path

from keen_eyes.models import Finding, GateStatus, ValidationResult


class SecretScanner:
    PATTERNS = [
        re.compile(r"AKIA[0-9A-Z]{16}"),
        re.compile(r"(?i)(api[_-]?key|secret|password)\s*=\s*['\"][^'\"]{12,}['\"]"),
        re.compile(r"-----BEGIN (RSA|OPENSSH|EC) PRIVATE KEY-----"),
    ]

    def scan(self, project_path: Path, out_dir: Path) -> ValidationResult:
        findings: list[Finding] = []
        for path in project_path.rglob("*"):
            if not path.is_file() or any(part.startswith(".") for part in path.parts):
                continue
            if path.suffix.lower() not in {".py", ".md", ".txt", ".json", ".yaml", ".yml", ".toml"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for pattern in self.PATTERNS:
                if pattern.search(text):
                    findings.append(
                        Finding(
                            id=f"SECRET-{len(findings) + 1}",
                            title="Potential secret detected",
                            severity="high",
                            status=GateStatus.FAIL,
                            detail=f"Potential secret pattern in {path.relative_to(project_path)}",
                            remediation="Remove the secret, rotate it, and use environment-backed configuration.",
                            control_objectives=["CM.L2-3.4.1[a]"],
                        )
                    )
        artifact = out_dir / "secret-scan.txt"
        artifact.write_text("\n".join(f.detail for f in findings) or "No secret patterns detected.", encoding="utf-8")
        return ValidationResult(
            id="secret-scan",
            name="Secret scan",
            category="security",
            status=GateStatus.FAIL if findings else GateStatus.PASS,
            summary=f"{len(findings)} potential secrets found",
            artifacts=[str(artifact)],
            findings=findings,
            control_objectives=["CM.L2-3.4.1[a]"],
        )

