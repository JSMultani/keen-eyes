import time
import unittest

from secure_document_workflow.service import DocumentWorkflow


class BenchmarkTests(unittest.TestCase):
    def test_list_documents_p95_under_budget(self):
        workflow = DocumentWorkflow.demo()
        author = workflow.login("author", "correct horse battery staple")
        for index in range(25):
            workflow.upload(author, f"doc-{index}.txt", b"content")
        durations = []
        for _ in range(100):
            start = time.perf_counter()
            workflow.list_documents(author)
            durations.append((time.perf_counter() - start) * 1000)
        p95 = sorted(durations)[94]
        self.assertLessEqual(p95, 50)

    def test_intentional_regression_budget_fixture(self):
        measured_p95 = 75
        budget = 50
        self.assertGreater(measured_p95, budget)


if __name__ == "__main__":
    unittest.main()

