import unittest
from pathlib import Path

from keen_eyes.orchestrator import RequirementsPlanner


class PlannerTests(unittest.TestCase):
    def test_sample_task_is_ready_and_extracts_budgets(self):
        plan = RequirementsPlanner().plan(Path("tasks/sample-feature.md"))
        self.assertTrue(plan.ready)
        self.assertEqual(plan.task.performance_budgets["list_documents_p95_ms"], 50)
        self.assertIn("AC.L1-3.1.1", plan.task.compliance_tags)


if __name__ == "__main__":
    unittest.main()

