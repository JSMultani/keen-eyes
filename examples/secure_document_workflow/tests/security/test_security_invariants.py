import unittest

from secure_document_workflow.service import AuthorizationError, DocumentWorkflow, ValidationError


class SecurityInvariantTests(unittest.TestCase):
    def test_unauthorized_download_is_denied_and_audited(self):
        workflow = DocumentWorkflow.demo()
        author = workflow.login("author", "correct horse battery staple")
        reader = workflow.login("reader", "correct horse battery staple")
        admin = workflow.login("admin", "correct horse battery staple")
        doc_id = workflow.upload(author, "private.txt", b"private")
        with self.assertRaises(AuthorizationError):
            workflow.download(reader, doc_id)
        self.assertIn("unauthorized_download", [event.event for event in workflow.audit_log(admin)])

    def test_log_redacts_sensitive_key_value_details(self):
        workflow = DocumentWorkflow.demo()
        workflow._record("test", "tester", "token=super-secret-value")
        self.assertNotIn("super-secret-value", workflow._audit[-1].detail)

    def test_control_characters_in_filename_are_rejected(self):
        workflow = DocumentWorkflow.demo()
        author = workflow.login("author", "correct horse battery staple")
        with self.assertRaises(ValidationError):
            workflow.upload(author, "bad\nname.txt", b"content")


if __name__ == "__main__":
    unittest.main()

