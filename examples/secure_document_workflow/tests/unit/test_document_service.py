import unittest

from secure_document_workflow.service import AuthorizationError, DocumentWorkflow, ValidationError


class DocumentServiceTests(unittest.TestCase):
    def setUp(self):
        self.workflow = DocumentWorkflow.demo()
        self.author = self.workflow.login("author", "correct horse battery staple")
        self.admin = self.workflow.login("admin", "correct horse battery staple")

    def test_author_can_upload_safe_document(self):
        doc_id = self.workflow.upload(self.author, "design.md", b"content")
        self.assertEqual(doc_id, 1)
        self.assertEqual(self.workflow.download(self.author, doc_id), b"content")

    def test_unsafe_filename_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.workflow.upload(self.author, "../secret.txt", b"content")

    def test_reader_cannot_upload(self):
        reader = self.workflow.login("reader", "correct horse battery staple")
        with self.assertRaises(AuthorizationError):
            self.workflow.upload(reader, "reader.md", b"content")

    def test_admin_can_read_audit_log(self):
        self.workflow.upload(self.author, "audit.md", b"content")
        events = [event.event for event in self.workflow.audit_log(self.admin)]
        self.assertIn("upload", events)


if __name__ == "__main__":
    unittest.main()

