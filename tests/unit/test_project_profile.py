import tempfile
import unittest
from pathlib import Path

from keen_eyes.project_profile import ProjectProfile


class ProjectProfileTests(unittest.TestCase):
    def test_loads_yaml_profile_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".keen-eyes.yaml").write_text(
                "project_type: node\ncommands:\n  test: \"npm test\"\n  security_test: \"npm run test:security\"\n",
                encoding="utf-8",
            )
            profile = ProjectProfile.load(root)
            self.assertEqual(profile.project_type, "node")
            self.assertEqual(profile.test_command, "npm test")
            self.assertEqual(profile.security_test_command, "npm run test:security")

    def test_infers_python_pytest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "tests").mkdir()
            (root / "tests" / "conftest.py").write_text("", encoding="utf-8")
            (root / "requirements.txt").write_text("pytest\n", encoding="utf-8")
            profile = ProjectProfile.load(root)
            self.assertEqual(profile.project_type, "python")
            self.assertEqual(profile.test_command, "python -m pytest")


if __name__ == "__main__":
    unittest.main()
