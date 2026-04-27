import unittest
from pathlib import Path

from keen_eyes.adapters import default_registry
from keen_eyes.models import GateStatus


FIXTURES = Path("tests/fixtures")


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.registry = default_registry()

    def test_junit_adapter_normalizes_failed_test(self):
        evidence = self.registry.parse("junit", FIXTURES / "junit.xml", "unit", "functional")
        self.assertEqual(len(evidence), 2)
        self.assertIn(GateStatus.FAIL, {item.status for item in evidence})

    def test_sarif_adapter_preserves_location(self):
        evidence = self.registry.parse("sarif", FIXTURES / "semgrep.sarif", "semgrep", "security")
        self.assertEqual(evidence[0].status, GateStatus.FAIL)
        self.assertEqual(evidence[0].location.file, "app/main.py")
        self.assertEqual(evidence[0].location.line, 42)

    def test_k6_adapter_fails_failed_threshold(self):
        evidence = self.registry.parse("k6", FIXTURES / "k6.json", "k6", "performance")
        self.assertEqual(evidence[0].status, GateStatus.FAIL)
        self.assertEqual(evidence[0].metrics["p95_ms"], 123.4)

    def test_osv_adapter_fails_vulnerabilities(self):
        evidence = self.registry.parse("osv", FIXTURES / "osv.json", "osv", "dependency")
        self.assertEqual(evidence[0].status, GateStatus.FAIL)
        self.assertIn("OSV-2026-1", evidence[0].title)

    def test_cyclonedx_adapter_records_sbom_and_vulns(self):
        evidence = self.registry.parse("cyclonedx", FIXTURES / "bom.json", "sbom", "supply_chain")
        self.assertEqual(evidence[0].status, GateStatus.PASS)
        self.assertEqual(evidence[1].status, GateStatus.FAIL)


if __name__ == "__main__":
    unittest.main()

