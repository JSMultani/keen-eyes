from __future__ import annotations

import ast
from pathlib import Path

from keen_eyes.models import Finding, GateStatus, ValidationResult


class StaticSecurityScanner:
    def scan(self, project_path: Path, out_dir: Path) -> ValidationResult:
        findings: list[Finding] = []
        for path in project_path.rglob("*.py"):
            if ".venv" in path.parts or "docs" in path.parts:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(text)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec"}:
                    self._add(
                        findings,
                        "Dangerous dynamic execution",
                        "high",
                        f"{node.func.id} call in {path.relative_to(project_path)}:{node.lineno}",
                        "Remove dynamic execution or replace with a constrained parser.",
                    )
            relative = path.relative_to(project_path)
            if "FastAPI(debug=True" in text:
                self._add(findings, "Debug mode enabled", "medium", f"Debug mode is enabled in {relative}", "Disable debug mode for any shared environment.")
            if 'allow_origins=["*"]' in text or "allow_origins=['*']" in text:
                self._add(findings, "Permissive CORS configuration", "medium", f"Wildcard CORS origin in {relative}", "Restrict allowed origins to known local origins for the benchmark.")
            if ".set_cookie(" in text and "httponly" not in text.lower():
                self._add(findings, "Session cookie missing hardening flags", "high", f"Cookie set without HttpOnly/SameSite/Secure flags in {relative}", "Set HttpOnly and SameSite flags, and Secure when using HTTPS.")
            if "password={password}" in text:
                self._add(findings, "Sensitive value recorded in audit detail", "high", f"Password variable appears in audit detail in {relative}", "Never log submitted passwords or session material.")
            if 'f"SELECT' in text or "f'SELECT" in text:
                self._add(findings, "SQL built with string interpolation", "high", f"Interpolated SQL query in {relative}", "Use parameterized SQL for user-controlled search values.")
            if "@app.get(\"/api/documents\")" in text and "current_user" not in text[text.find("@app.get(\"/api/documents\")") :]:
                self._add(findings, "Unauthenticated document API exposure", "high", f"Document API route lacks authentication check in {relative}", "Require authentication and authorization before returning document data.")
            if "UploadFile" in text and "file.filename" in text and "write_text" in text:
                self._add(findings, "Weak file upload validation", "high", f"Upload handler stores user-supplied filename in {relative}", "Validate file names, size, and content type before storing uploads.")

        for path in (project_path / "app" / "templates").rglob("*.html") if (project_path / "app" / "templates").exists() else []:
            text = path.read_text(encoding="utf-8", errors="ignore")
            if "|safe" in text:
                self._add(
                    findings,
                    "Template disables output escaping",
                    "medium",
                    f"Template uses safe filter in {path.relative_to(project_path)}",
                    "Remove unsafe rendering for user-controlled content or sanitize before rendering.",
                )
        artifact = out_dir / "static-security-scan.txt"
        artifact.write_text("\n".join(f"{f.severity}: {f.detail}" for f in findings) or "No static security findings detected.", encoding="utf-8")
        return ValidationResult(
            id="static-security-scan",
            name="Static security scan",
            category="security",
            status=GateStatus.FAIL if findings else GateStatus.PASS,
            summary=f"{len(findings)} static security findings",
            artifacts=[str(artifact)],
            findings=findings,
            control_objectives=["CM.L2-3.4.1[a]"],
        )

    def _add(self, findings: list[Finding], title: str, severity: str, detail: str, remediation: str) -> None:
        findings.append(
            Finding(
                id=f"STATIC-{len(findings) + 1}",
                title=title,
                severity=severity,
                status=GateStatus.FAIL,
                detail=detail,
                remediation=remediation,
                control_objectives=["CM.L2-3.4.1[a]"],
            )
        )
