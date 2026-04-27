import tempfile
import unittest
from pathlib import Path

from keen_eyes.compliance import ComplianceEvidenceEngine
from keen_eyes.models.core import GateStatus, TaskSpec, ValidationResult
from keen_eyes.storage import FileEvidenceStore


class ComplianceTests(unittest.TestCase):
    def test_interview_objective_requires_human_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            artifact = Path(tmp) / "scan.txt"
            artifact.write_text("ok", encoding="utf-8")
            task = TaskSpec("T-1", "Task", ["do"], ["fast"], ["secure"], {"p95": 1}, ["AC.L1-3.1.1"], "task.md")
            result = ValidationResult("security-tests", "Security", "security", GateStatus.PASS, "ok", [str(artifact)], [], {}, ["AC.L1-3.1.1[a]"])
            manifest = ComplianceEvidenceEngine().generate_manifest("run", task, [result], FileEvidenceStore(Path(tmp)))
            statuses = {control.objective_id: control.status.value for control in manifest.control_results}
            self.assertEqual(statuses["AC.L1-3.1.1[b]"], "human_review_required")
            self.assertEqual(statuses["AC.L1-3.1.1[a]"], "automated_pass")


if __name__ == "__main__":
    unittest.main()

