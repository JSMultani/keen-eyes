import unittest

from secure_document_workflow.service import AuthorizationError, DocumentWorkflow


class WorkflowTests(unittest.TestCase):
    def test_approval_workflow_allows_reader_after_approval(self):
        workflow = DocumentWorkflow.demo()
        author = workflow.login("author", "correct horse battery staple")
        approver = workflow.login("approver", "correct horse battery staple")
        reader = workflow.login("reader", "correct horse battery staple")
        doc_id = workflow.upload(author, "policy.pdf", b"policy")

        with self.assertRaises(AuthorizationError):
            workflow.download(reader, doc_id)

        workflow.approve(approver, doc_id)
        self.assertEqual(workflow.download(reader, doc_id), b"policy")

    def test_admin_view_contains_security_events(self):
        workflow = DocumentWorkflow.demo()
        author = workflow.login("author", "correct horse battery staple")
        reader = workflow.login("reader", "correct horse battery staple")
        admin = workflow.login("admin", "correct horse battery staple")
        doc_id = workflow.upload(author, "plan.txt", b"plan")
        with self.assertRaises(AuthorizationError):
            workflow.download(reader, doc_id)
        events = [event.event for event in workflow.audit_log(admin)]
        self.assertIn("unauthorized_download", events)


if __name__ == "__main__":
    unittest.main()

