import tempfile
import unittest
from pathlib import Path

from keen_eyes.orchestrator import Orchestrator


class OrchestratorTests(unittest.TestCase):
    def test_demo_run_generates_reports(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            report = Orchestrator().run(
                Path("tasks/sample-feature.md"),
                Path("examples/secure_document_workflow"),
                out,
                "test-run",
            )
            self.assertTrue(report.passed)
            self.assertTrue((out / "evidence-manifest.json").exists())
            self.assertTrue((out / "validation-report.md").exists())
            self.assertTrue((out / "poam.json").exists())


if __name__ == "__main__":
    unittest.main()

