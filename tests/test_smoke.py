"""Smoke tests for CHECKPOINT-AI. No network. Run: python -m pytest tests/ or python tests/test_smoke.py"""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from checkpoint_ai import (  # noqa: E402
    TOOL_NAME,
    TOOL_VERSION,
    Assessment,
    assess,
    classify_eu_risk_tier,
    generate_ssp,
)
from checkpoint_ai.cli import main  # noqa: E402
from checkpoint_ai.core import (  # noqa: E402
    AssessmentError,
    CONTROL_CATALOG,
    load_assessment_dict,
)


DEMO = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "demos",
    "01-basic",
    "assessment.json",
)


class TestCore(unittest.TestCase):
    def test_metadata(self):
        self.assertEqual(TOOL_NAME, "CHECKPOINT-AI")
        self.assertTrue(TOOL_VERSION)

    def test_eu_tier_classification(self):
        self.assertEqual(classify_eu_risk_tier(["social_scoring"], "x"), "unacceptable")
        self.assertEqual(classify_eu_risk_tier(["employment_screening"], "x"), "high")
        self.assertEqual(classify_eu_risk_tier(["chatbot"], "x"), "limited")
        self.assertEqual(classify_eu_risk_tier([], "x"), "minimal")
        # highest tier wins when multiple apply
        self.assertEqual(
            classify_eu_risk_tier(["chatbot", "law_enforcement"], "x"), "high"
        )

    def test_perfect_score(self):
        resp = {c["id"]: "verified" for c in CONTROL_CATALOG}
        a = Assessment(system_name="s", owner="o", purpose="p", responses=resp)
        r = assess(a)
        self.assertEqual(r.overall_score, 100.0)
        self.assertEqual(r.maturity, "Optimized")
        self.assertEqual(r.gaps, [])

    def test_empty_is_initial_with_gaps(self):
        a = Assessment(system_name="s", owner="o", purpose="p", responses={})
        r = assess(a)
        self.assertEqual(r.overall_score, 0.0)
        self.assertEqual(r.maturity, "Initial")
        self.assertEqual(len(r.gaps), len(CONTROL_CATALOG))

    def test_not_applicable_excluded(self):
        resp = {c["id"]: "verified" for c in CONTROL_CATALOG}
        resp["GOV-3"] = "not_applicable"
        a = Assessment(system_name="s", owner="o", purpose="p", responses=resp)
        r = assess(a)
        # N/A control still scores 100 overall (excluded from denominator)
        self.assertEqual(r.overall_score, 100.0)
        na = [c for c in r.controls if c.control_id == "GOV-3"][0]
        self.assertFalse(na.applicable)
        self.assertNotIn("GOV-3", r.gaps)

    def test_invalid_status_raises(self):
        a = Assessment(system_name="s", owner="o", purpose="p", responses={"GOV-1": "bogus"})
        with self.assertRaises(AssessmentError):
            assess(a)

    def test_load_rejects_unknown_control(self):
        with self.assertRaises(AssessmentError):
            load_assessment_dict({"system_name": "s", "responses": {"ZZZ-9": "verified"}})

    def test_load_requires_system_name(self):
        with self.assertRaises(AssessmentError):
            load_assessment_dict({"responses": {}})

    def test_ssp_poam_prioritizes_high(self):
        a = load_assessment_dict(json.load(open(DEMO, encoding="utf-8")))
        r = assess(a)
        ssp = generate_ssp(r, purpose=a.purpose)
        poam = ssp["plan_of_action_and_milestones"]
        self.assertTrue(poam)
        # high-priority items come first
        priorities = [p["priority"] for p in poam]
        self.assertEqual(priorities, sorted(priorities, key=lambda x: 0 if x == "high" else 1))
        self.assertEqual(ssp["oscal_flavor"], "system-security-plan")


class TestCli(unittest.TestCase):
    def test_catalog_json(self):
        self.assertEqual(main(["--format", "json", "catalog"]), 0)

    def test_assess_demo_nonzero_on_high_gap(self):
        # demo has weight-5 gaps (MEA-2, MAN-1) -> exit 2
        self.assertEqual(main(["--format", "json", "assess", DEMO]), 2)

    def test_ssp_demo_ok(self):
        self.assertEqual(main(["--format", "json", "ssp", DEMO]), 0)

    def test_missing_file_returns_1(self):
        self.assertEqual(main(["assess", "/nonexistent/path.json"]), 1)

    def test_assess_all_verified_zero_exit(self):
        resp = {c["id"]: "verified" for c in CONTROL_CATALOG}
        doc = {"system_name": "s", "owner": "o", "responses": resp}
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as fh:
            json.dump(doc, fh)
            path = fh.name
        try:
            self.assertEqual(main(["assess", path]), 0)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
