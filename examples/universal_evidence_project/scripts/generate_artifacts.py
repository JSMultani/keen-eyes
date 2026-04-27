from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports"


def main() -> int:
    REPORTS.mkdir(exist_ok=True)
    (REPORTS / "junit.xml").write_text(
        """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<testsuite tests=\"1\" failures=\"0\" errors=\"0\" skipped=\"0\">
  <testcase classname=\"tests.test_demo\" name=\"test_dummy_business_rule\" time=\"0.01\" />
</testsuite>
""",
        encoding="utf-8",
    )
    (REPORTS / "semgrep.sarif").write_text(
        json.dumps(
            {
                "version": "2.1.0",
                "runs": [
                    {
                        "tool": {"driver": {"name": "Semgrep", "rules": [{"id": "demo.warning", "name": "Demo warning"}]}},
                        "results": [],
                    }
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (REPORTS / "k6.json").write_text(
        json.dumps(
            {
                "metrics": {
                    "http_req_duration": {
                        "values": {"p(95)": 42.0},
                        "thresholds": {"p(95)<100": {"ok": True}},
                    }
                },
                "root_group": {"checks": [{"name": "status is 200", "passes": 20, "fails": 0}]},
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (REPORTS / "osv.json").write_text(json.dumps({"results": []}, indent=2), encoding="utf-8")
    (REPORTS / "bom.json").write_text(
        json.dumps(
            {
                "bomFormat": "CycloneDX",
                "specVersion": "1.5",
                "components": [{"type": "library", "name": "demo-lib", "version": "1.0.0"}],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
