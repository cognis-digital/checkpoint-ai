"""Tests for the SARIF 2.1.0 and CSV finding exporters. No network."""
import csv
import io
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from checkpoint_ai.cli import main  # noqa: E402
from checkpoint_ai.core import (  # noqa: E402
    CONTROL_CATALOG,
    Assessment,
    assess,
    to_csv,
    to_sarif,
)

DEMO_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "demos"
)


def _result_with_gaps():
    # Two controls left as gaps: one weight-5 (MEA-2), one weight-3 (GOV-3).
    resp = {c["id"]: "verified" for c in CONTROL_CATALOG}
    resp["MEA-2"] = "not_started"  # weight 5 -> sarif error
    resp["GOV-3"] = "partial"      # weight 3 -> sarif warning
    a = Assessment(system_name="sys", owner="o", purpose="p", responses=resp)
    return assess(a)


class TestSarif(unittest.TestCase):
    def test_sarif_skeleton(self):
        r = _result_with_gaps()
        s = to_sarif(r)
        self.assertEqual(s["version"], "2.1.0")
        self.assertIn("sarif-2.1.0", s["$schema"])
        self.assertEqual(len(s["runs"]), 1)
        driver = s["runs"][0]["tool"]["driver"]
        self.assertEqual(driver["name"], "CHECKPOINT-AI")
        # one rule per catalog control
        self.assertEqual(len(driver["rules"]), len(CONTROL_CATALOG))

    def test_sarif_results_match_gaps(self):
        r = _result_with_gaps()
        s = to_sarif(r)
        results = s["runs"][0]["results"]
        rule_ids = {res["ruleId"] for res in results}
        self.assertEqual(rule_ids, set(r.gaps))
        self.assertEqual(len(results), len(r.gaps))

    def test_sarif_levels_and_severity(self):
        r = _result_with_gaps()
        s = to_sarif(r)
        by_id = {res["ruleId"]: res for res in s["runs"][0]["results"]}
        self.assertEqual(by_id["MEA-2"]["level"], "error")   # weight 5
        self.assertEqual(by_id["GOV-3"]["level"], "warning")  # weight 3
        sev = float(by_id["MEA-2"]["properties"]["security-severity"])
        self.assertTrue(0.0 <= sev <= 10.0)
        # framework crosswalk preserved on the result
        self.assertEqual(
            by_id["MEA-2"]["properties"]["framework:eu_ai_act"], "Art.10"
        )

    def test_sarif_run_properties(self):
        r = _result_with_gaps()
        props = to_sarif(r)["runs"][0]["properties"]
        self.assertEqual(props["system_name"], "sys")
        self.assertIn("eu_ai_act_risk_tier", props)

    def test_sarif_clean_assessment_has_no_results(self):
        resp = {c["id"]: "verified" for c in CONTROL_CATALOG}
        a = Assessment(system_name="clean", owner="o", purpose="p", responses=resp)
        s = to_sarif(assess(a))
        self.assertEqual(s["runs"][0]["results"], [])
        # rules are still emitted even with zero findings
        self.assertEqual(len(s["runs"][0]["tool"]["driver"]["rules"]), len(CONTROL_CATALOG))

    def test_sarif_validates_against_schema_if_available(self):
        try:
            import jsonschema  # noqa: F401
        except ImportError:
            self.skipTest("jsonschema not installed")
        from jsonschema import Draft7Validator

        s = to_sarif(_result_with_gaps())
        # Minimal structural contract that any SARIF 2.1.0 consumer relies on.
        contract = {
            "type": "object",
            "required": ["version", "runs"],
            "properties": {
                "version": {"const": "2.1.0"},
                "runs": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "required": ["tool", "results"],
                        "properties": {
                            "tool": {
                                "type": "object",
                                "required": ["driver"],
                                "properties": {
                                    "driver": {
                                        "type": "object",
                                        "required": ["name", "rules"],
                                    }
                                },
                            },
                            "results": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "required": ["ruleId", "level", "message"],
                                },
                            },
                        },
                    },
                },
            },
        }
        Draft7Validator(contract).validate(s)


class TestCsv(unittest.TestCase):
    def test_csv_one_row_per_control(self):
        r = _result_with_gaps()
        text = to_csv(r)
        rows = list(csv.DictReader(io.StringIO(text)))
        self.assertEqual(len(rows), len(CONTROL_CATALOG))

    def test_csv_header_and_gap_flag(self):
        r = _result_with_gaps()
        rows = list(csv.DictReader(io.StringIO(to_csv(r))))
        by_id = {row["control_id"]: row for row in rows}
        self.assertEqual(by_id["MEA-2"]["is_gap"], "True")
        self.assertTrue(by_id["MEA-2"]["remediation"])  # gap has remediation text
        # non-gap rows carry no remediation
        self.assertEqual(by_id["GOV-1"]["is_gap"], "False")
        self.assertEqual(by_id["GOV-1"]["remediation"], "")
        # crosswalk columns present
        self.assertEqual(by_id["MEA-2"]["eu_ai_act"], "Art.10")


class TestCliFormats(unittest.TestCase):
    def _demo(self, name):
        return os.path.join(DEMO_DIR, name, "self-assessment.json")

    def test_cli_sarif_exit_and_parses(self):
        # high-risk CI demo has a weight-5 gap -> exit 2, valid JSON SARIF
        import contextlib

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = main(["--format", "sarif", "assess", self._demo("09-ci-sarif-gate")])
        self.assertEqual(rc, 2)
        doc = json.loads(buf.getvalue())
        self.assertEqual(doc["version"], "2.1.0")

    def test_cli_csv_parses(self):
        import contextlib

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = main(["--format", "csv", "assess", self._demo("06-internal-analytics-minimal")])
        self.assertEqual(rc, 0)  # minimal-risk demo, no weight-5 gap
        rows = list(csv.DictReader(io.StringIO(buf.getvalue())))
        self.assertEqual(len(rows), len(CONTROL_CATALOG))


if __name__ == "__main__":
    unittest.main(verbosity=2)
