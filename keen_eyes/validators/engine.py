from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

from keen_eyes.models import Finding, GateStatus, RequirementPlan, ValidationResult
from keen_eyes.project_profile import ProjectProfile
from keen_eyes.scanners.dependency import DependencyScanner
from keen_eyes.scanners.secret import SecretScanner
from keen_eyes.scanners.static_security import StaticSecurityScanner


class ValidationEngine:
    def __init__(self) -> None:
        self.secret_scanner = SecretScanner()
        self.dependency_scanner = DependencyScanner()
        self.static_scanner = StaticSecurityScanner()

    def run_all(self, project_path: Path, plan: RequirementPlan, out_dir: Path, profile: ProjectProfile) -> list[ValidationResult]:
        project_path = project_path.resolve()
        results = [
            self.run_tests(project_path, out_dir, profile),
            self.run_security_tests(project_path, out_dir, profile),
            self.run_benchmark(project_path, plan, out_dir, profile),
            self.static_scanner.scan(project_path, out_dir),
            self.secret_scanner.scan(project_path, out_dir),
            self.dependency_scanner.scan(project_path, out_dir),
        ]
        results.extend(self.run_profile_scanners(project_path, out_dir, profile))
        return results

    def run_tests(self, project_path: Path, out_dir: Path, profile: ProjectProfile) -> ValidationResult:
        project_path = project_path.resolve()
        artifact = out_dir / "unit-integration-tests.txt"
        command = profile.test_command
        if not command:
            finding = Finding(
                id="TEST-001",
                title="No functional test command configured",
                severity="high",
                status=GateStatus.FAIL,
                detail=f"No test command could be inferred for project type {profile.project_type}.",
                remediation="Add .keen-eyes.yaml with commands.test for this project.",
                control_objectives=["AC.L1-3.1.1[a]"],
            )
            artifact.write_text(finding.detail, encoding="utf-8")
            return ValidationResult(
                id="unit-integration-tests",
                name="Unit and integration tests",
                category="functional",
                status=GateStatus.FAIL,
                summary="No test command configured",
                artifacts=[str(artifact)],
                findings=[finding],
                control_objectives=["AC.L1-3.1.1[a]", "AU.L2-3.3.1[b]"],
            )
        result = subprocess.run(
            command,
            cwd=project_path,
            shell=True,
            capture_output=True,
            text=True,
            check=False,
        )
        artifact.write_text(result.stdout + result.stderr, encoding="utf-8")
        status = GateStatus.PASS if result.returncode == 0 else GateStatus.FAIL
        return ValidationResult(
            id="unit-integration-tests",
            name="Unit and integration tests",
            category="functional",
            status=status,
            summary=f"{command} exit code {result.returncode}",
            artifacts=[str(artifact)],
            control_objectives=["AC.L1-3.1.1[a]", "AU.L2-3.3.1[b]"],
        )

    def run_security_tests(self, project_path: Path, out_dir: Path, profile: ProjectProfile) -> ValidationResult:
        project_path = project_path.resolve()
        artifact = out_dir / "security-tests.txt"
        if not profile.security_test_command:
            finding = Finding(
                id="SEC-TEST-001",
                title="No dedicated negative security test suite",
                severity="medium",
                status=GateStatus.FAIL,
                detail="Project does not contain tests/security with negative authorization or input-handling tests.",
                remediation="Add negative tests for unauthorized access, unsafe input handling, upload validation, and sensitive log handling.",
                control_objectives=["AC.L1-3.1.1[a]"],
            )
            artifact.write_text(finding.detail, encoding="utf-8")
            return ValidationResult(
                id="security-tests",
                name="Negative security tests",
                category="security",
                status=GateStatus.FAIL,
                summary="No tests/security suite found",
                artifacts=[str(artifact)],
                findings=[finding],
                control_objectives=["AC.L1-3.1.1[a]"],
            )
        result = subprocess.run(
            profile.security_test_command,
            cwd=project_path,
            shell=True,
            capture_output=True,
            text=True,
            check=False,
        )
        artifact.write_text(result.stdout + result.stderr, encoding="utf-8")
        status = GateStatus.PASS if result.returncode == 0 else GateStatus.FAIL
        return ValidationResult(
            id="security-tests",
            name="Negative security tests",
            category="security",
            status=status,
            summary=f"{profile.security_test_command} exit code {result.returncode}",
            artifacts=[str(artifact)],
            control_objectives=["AC.L1-3.1.1[a]"],
        )

    def run_benchmark(self, project_path: Path, plan: RequirementPlan, out_dir: Path, profile: ProjectProfile) -> ValidationResult:
        project_path = project_path.resolve()
        if profile.benchmark_command:
            artifact = out_dir / "benchmark.txt"
            result = subprocess.run(
                profile.benchmark_command,
                cwd=project_path,
                shell=True,
                capture_output=True,
                text=True,
                check=False,
            )
            artifact.write_text(result.stdout + result.stderr, encoding="utf-8")
            status = GateStatus.PASS if result.returncode == 0 else GateStatus.FAIL
            findings = []
            if status == GateStatus.FAIL:
                findings.append(
                    Finding(
                        id="PERF-001",
                        title="Benchmark command failed",
                        severity="medium",
                        status=status,
                        detail=f"{profile.benchmark_command} exited {result.returncode}",
                        remediation="Fix the benchmark or update the configured performance budget.",
                    )
                )
            return ValidationResult(
                id="performance-benchmark",
                name="Configured performance benchmark",
                category="performance",
                status=status,
                summary=f"{profile.benchmark_command} exit code {result.returncode}",
                artifacts=[str(artifact)],
                findings=findings,
            )
        if (project_path / "secure_document_workflow").exists():
            import sys

            sys.path.insert(0, str(project_path))
            try:
                from secure_document_workflow.service import DocumentWorkflow

                workflow = DocumentWorkflow.demo()
                durations: list[float] = []
                for _ in range(150):
                    start = time.perf_counter()
                    workflow.list_documents("author")
                    durations.append((time.perf_counter() - start) * 1000)
            finally:
                if str(project_path) in sys.path:
                    sys.path.remove(str(project_path))
        elif (project_path / "app" / "main.py").exists():
            import sys

            sys.path.insert(0, str(project_path))
            try:
                from fastapi.testclient import TestClient

                from app.main import app

                client = TestClient(app)
                client.post("/login", data={"username": "employee", "password": "employee123"}, follow_redirects=False)
                durations = []
                for _ in range(75):
                    start = time.perf_counter()
                    response = client.get("/documents")
                    response.read()
                    durations.append((time.perf_counter() - start) * 1000)
            finally:
                if str(project_path) in sys.path:
                    sys.path.remove(str(project_path))
        else:
            durations = [0.0]
        p95 = sorted(durations)[int(len(durations) * 0.95) - 1]
        budget = plan.task.performance_budgets.get("list_documents_p95_ms", 50.0)
        status = GateStatus.PASS if p95 <= budget else GateStatus.FAIL
        artifact = out_dir / "benchmark.json"
        artifact.write_text(json.dumps({"list_documents_p95_ms": p95, "budget_ms": budget}, indent=2), encoding="utf-8")
        findings = []
        if status == GateStatus.FAIL:
            findings.append(
                Finding(
                    id="PERF-001",
                    title="Document listing exceeded p95 budget",
                    severity="medium",
                    status=status,
                    detail=f"p95 {p95:.3f} ms exceeded budget {budget:.3f} ms",
                    remediation="Profile document listing and reduce per-request work.",
                )
            )
        return ValidationResult(
            id="performance-benchmark",
            name="Document listing p95 benchmark",
            category="performance",
            status=status,
            summary=f"p95={p95:.3f} ms budget={budget:.3f} ms",
            artifacts=[str(artifact)],
            findings=findings,
            metrics={"list_documents_p95_ms": p95},
        )

    def run_profile_scanners(self, project_path: Path, out_dir: Path, profile: ProjectProfile) -> list[ValidationResult]:
        results: list[ValidationResult] = []
        for name, command in sorted(profile.scanner_commands.items()):
            artifact = out_dir / f"profile-scanner-{name}.txt"
            result = subprocess.run(
                command,
                cwd=project_path,
                shell=True,
                capture_output=True,
                text=True,
                check=False,
            )
            artifact.write_text(result.stdout + result.stderr, encoding="utf-8")
            status = GateStatus.PASS if result.returncode == 0 else GateStatus.FAIL
            findings = []
            if status == GateStatus.FAIL:
                findings.append(
                    Finding(
                        id=f"SCANNER-{name.upper()}",
                        title=f"Profile scanner failed: {name}",
                        severity="medium",
                        status=status,
                        detail=f"{command} exited {result.returncode}",
                        remediation="Review scanner output and remediate or document accepted risk.",
                        control_objectives=["SI.L2-3.14.1[a]"],
                    )
                )
            results.append(
                ValidationResult(
                    id=f"profile-scanner-{name}",
                    name=f"Profile scanner: {name}",
                    category="security",
                    status=status,
                    summary=f"{command} exit code {result.returncode}",
                    artifacts=[str(artifact)],
                    findings=findings,
                    control_objectives=["SI.L2-3.14.1[a]"],
                )
            )
        return results
