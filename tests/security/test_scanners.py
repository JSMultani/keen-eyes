import tempfile
import unittest
from pathlib import Path

from keen_eyes.models.core import GateStatus
from keen_eyes.scanners.secret import SecretScanner


class ScannerTests(unittest.TestCase):
    def test_secret_scanner_fails_on_secret_pattern(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "app.py").write_text("api_key = 'abcdefghijklmnopqrstuvwxyz'\n", encoding="utf-8")
            result = SecretScanner().scan(root, root)
            self.assertEqual(result.status, GateStatus.FAIL)


if __name__ == "__main__":
    unittest.main()

