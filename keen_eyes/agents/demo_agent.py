from __future__ import annotations

import subprocess
from pathlib import Path

from keen_eyes.agents.base import CodingAgent
from keen_eyes.models import RequirementPlan
from keen_eyes.project_profile import ProjectProfile


class DeterministicDemoAgent(CodingAgent):
    """MVP agent that verifies a project has test-first artifacts without model calls."""

    REQUIRED_TESTS = [
        "tests/unit/test_document_service.py",
        "tests/integration/test_workflow.py",
        "tests/security/test_security_invariants.py",
        "tests/performance/test_benchmark.py",
    ]

    def execute(self, plan: RequirementPlan, project_path: Path, out_dir: Path, profile: ProjectProfile) -> list[dict[str, str]]:
        project_path = project_path.resolve()
        trace: list[dict[str, str]] = [
            {"phase": "red", "detail": "Acceptance criteria and failing test targets derived before implementation."}
        ]

        if (project_path / "secure_document_workflow").exists():
            missing = [path for path in self.REQUIRED_TESTS if not (project_path / path).exists()]
            if missing:
                raise FileNotFoundError("Demo project missing required TDD tests: " + ", ".join(missing))
            test_command = profile.test_command or "python -m unittest discover -s tests"
            trace.append({"phase": "green", "detail": "Strict secure_document_workflow TDD test set is present."})
        else:
            test_files = sorted((project_path / "tests").rglob("test_*.py")) if (project_path / "tests").exists() else []
            if not test_files:
                raise FileNotFoundError("Project is missing discoverable tests under tests/test_*.py")
            if not profile.test_command:
                raise FileNotFoundError("Project has tests but no runnable test command could be inferred. Add .keen-eyes.yaml.")
            test_command = profile.test_command
            trace.append({"phase": "green", "detail": f"Found {len(test_files)} project test file(s) before validation."})

        trace.append({"phase": "refactor", "detail": "No behavior-changing refactor required for MVP demo run."})
        result = subprocess.run(
            test_command,
            cwd=project_path,
            shell=True,
            capture_output=True,
            text=True,
            check=False,
        )
        (out_dir / "agent-test-precheck.txt").write_text(result.stdout + result.stderr, encoding="utf-8")
        trace.append({"phase": "verify", "detail": f"Agent precheck exit code {result.returncode}."})
        return trace
