import tempfile
import unittest
from pathlib import Path

from keen_eyes.project_profile import ProjectProfile


class ProjectProfileTests(unittest.TestCase):
    def test_loads_yaml_profile_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".keen-eyes.yaml").write_text(
                "\n".join(
                    [
                        "project_type: node",
                        "commands:",
                        "  test: \"npm test\"",
                        "  security_test: \"npm run test:security\"",
                        "artifacts:",
                        "  - name: unit",
                        "    path: reports/junit.xml",
                        "    format: junit",
                        "    category: functional",
                        "    controls: \"AC.L1-3.1.1[a]\"",
                    ]
                ),
                encoding="utf-8",
            )
            profile = ProjectProfile.load(root)
            self.assertEqual(profile.project_type, "node")
            self.assertEqual(profile.test_command, "npm test")
            self.assertEqual(profile.security_test_command, "npm run test:security")
            self.assertEqual(profile.artifacts[0].format, "junit")
            self.assertEqual(profile.artifacts[0].control_objectives, ["AC.L1-3.1.1[a]"])

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
