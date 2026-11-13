"""Regression tests for structured qualification report rendering."""
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from qualification.report import TEMPLATE, render


class QualificationReportTemplateTests(unittest.TestCase):
    def test_report_is_rendered_from_external_template(self):
        template = TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("$case_rows", template)
        self.assertIn("$image_sections", template)

        result = {
            "schema_version": 1,
            "source_commit": "abc123",
            "solidcraft_version": "0.30.1",
            "cases": {
                "demo": {
                    "title": "Demo case",
                    "status": "pass",
                    "levels": {
                        "q1": {"status": "pass"},
                        "q2": {"status": "pass"},
                        "q3": {"status": "pass"},
                        "q4": {"status": "pass"},
                        "q5": {"status": "not-required"},
                        "q6": {"status": "pass", "images": ["model.png"]},
                    },
                }
            },
        }

        report = render(result)

        self.assertIn("# SCPF Forge qualification", report)
        self.assertIn("abc123", report)
        self.assertIn("0.30.1", report)
        self.assertIn("| `demo` | PASS | PASS | PASS | PASS | PASS | N/R | PASS |", report)
        self.assertIn("../native/demo/model.png", report)
        self.assertIn("qualification/templates/report.md", report)


if __name__ == "__main__":
    unittest.main()
