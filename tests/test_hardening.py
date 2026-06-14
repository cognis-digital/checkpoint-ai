"""Hardening tests: error paths, edge cases, and bad-input handling."""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from checkpoint_ai.core import (
    AssessmentError,
    Assessment,
    CONTROL_CATALOG,
    assess,
    classify_eu_risk_tier,
    load_assessment,
    load_assessment_dict,
)
from checkpoint_ai.cli import main


# ---------------------------------------------------------------------------
# load_assessment_dict — input validation
# ---------------------------------------------------------------------------


class TestLoadAssessmentDictValidation(unittest.TestCase):
    def test_non_dict_raises(self):
        with self.assertRaises(AssessmentError):
            load_assessment_dict([])

    def test_null_system_name_raises(self):
        with self.assertRaises(AssessmentError):
            load_assessment_dict({"system_name": None})

    def test_blank_system_name_raises(self):
        with self.assertRaises(AssessmentError):
            load_assessment_dict({"system_name": "   "})

    def test_eu_use_cases_not_list_raises(self):
        with self.assertRaises(AssessmentError):
            load_assessment_dict({"system_name": "s", "eu_use_cases": "chatbot"})

    def test_eu_use_cases_non_string_item_raises(self):
        with self.assertRaises(AssessmentError):
            load_assessment_dict({"system_name": "s", "eu_use_cases": [42]})

    def test_responses_not_dict_raises(self):
        with self.assertRaises(AssessmentError):
            load_assessment_dict({"system_name": "s", "responses": ["GOV-1"]})

    def test_empty_responses_defaults_all_not_started(self):
        a = load_assessment_dict({"system_name": "s"})
        self.assertEqual(a.system_name, "s")
        self.assertEqual(a.responses, {})

    def test_system_name_stripped(self):
        a = load_assessment_dict({"system_name": "  my system  "})
        self.assertEqual(a.system_name, "my system")


# ---------------------------------------------------------------------------
# load_assessment — file I/O error paths
# ---------------------------------------------------------------------------


class TestLoadAssessmentFileErrors(unittest.TestCase):
    def test_missing_file_raises_assessment_error(self):
        with self.assertRaises(AssessmentError) as ctx:
            load_assessment("/nonexistent/path/file.json")
        self.assertIn("not found", str(ctx.exception))

    def test_directory_path_raises_assessment_error(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(AssessmentError):
                # On POSIX this is IsADirectoryError; on Windows PermissionError.
                # Either way it must be an AssessmentError, not a raw OSError.
                load_assessment(d)

    def test_malformed_json_raises_assessment_error(self):
        with tempfile.NamedTemporaryFile(
            "w", suffix=".json", delete=False, encoding="utf-8"
        ) as fh:
            fh.write("{not valid json ...")
            path = fh.name
        try:
            with self.assertRaises(AssessmentError) as ctx:
                load_assessment(path)
            self.assertIn("invalid JSON", str(ctx.exception))
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# assess() — edge cases
# ---------------------------------------------------------------------------


class TestAssessEdgeCases(unittest.TestCase):
    def test_blank_system_name_raises(self):
        a = Assessment(system_name="", owner="o", purpose="p")
        with self.assertRaises(AssessmentError):
            assess(a)

    def test_whitespace_only_system_name_raises(self):
        a = Assessment(system_name="   ", owner="o", purpose="p")
        with self.assertRaises(AssessmentError):
            assess(a)

    def test_all_not_applicable_produces_zero_score(self):
        resp = {c["id"]: "not_applicable" for c in CONTROL_CATALOG}
        a = Assessment(system_name="s", owner="o", purpose="p", responses=resp)
        r = assess(a)
        # All N/A: total_max=0 -> overall_score falls back to 0.0
        self.assertEqual(r.overall_score, 0.0)
        self.assertEqual(r.gaps, [])

    def test_partial_responses_produce_gaps(self):
        # Only fill in one control as verified; rest default to not_started (gaps)
        a = Assessment(
            system_name="s", owner="o", purpose="p", responses={"GOV-1": "verified"}
        )
        r = assess(a)
        self.assertNotIn("GOV-1", r.gaps)
        # All other controls should be gaps
        self.assertEqual(len(r.gaps), len(CONTROL_CATALOG) - 1)


# ---------------------------------------------------------------------------
# classify_eu_risk_tier — defensive handling
# ---------------------------------------------------------------------------


class TestClassifyEuRiskTierDefensive(unittest.TestCase):
    def test_none_input_returns_minimal(self):
        # None is not a list; should coerce to [] and return minimal
        result = classify_eu_risk_tier(None, "x")  # type: ignore[arg-type]
        self.assertEqual(result, "minimal")

    def test_empty_list_returns_minimal(self):
        self.assertEqual(classify_eu_risk_tier([], "x"), "minimal")


# ---------------------------------------------------------------------------
# CLI — exit codes and error messages
# ---------------------------------------------------------------------------


class TestCliHardening(unittest.TestCase):
    def test_missing_file_exit_1(self):
        self.assertEqual(main(["assess", "/no/such/file.json"]), 1)

    def test_missing_file_ssp_exit_1(self):
        self.assertEqual(main(["ssp", "/no/such/file.json"]), 1)

    def test_malformed_json_exits_1(self):
        with tempfile.NamedTemporaryFile(
            "w", suffix=".json", delete=False, encoding="utf-8"
        ) as fh:
            fh.write("{broken json")
            path = fh.name
        try:
            self.assertEqual(main(["assess", path]), 1)
        finally:
            os.unlink(path)

    def test_missing_system_name_exits_1(self):
        with tempfile.NamedTemporaryFile(
            "w", suffix=".json", delete=False, encoding="utf-8"
        ) as fh:
            json.dump({"owner": "o", "responses": {}}, fh)
            path = fh.name
        try:
            self.assertEqual(main(["assess", path]), 1)
        finally:
            os.unlink(path)

    def test_directory_as_input_exits_1_or_2(self):
        # Passing a directory path must not traceback — it must exit non-zero.
        with tempfile.TemporaryDirectory() as d:
            result = main(["assess", d])
        self.assertNotEqual(result, 0)

    def test_all_verified_ssp_exit_0(self):
        resp = {c["id"]: "verified" for c in CONTROL_CATALOG}
        doc = {"system_name": "s", "owner": "o", "responses": resp}
        with tempfile.NamedTemporaryFile(
            "w", suffix=".json", delete=False, encoding="utf-8"
        ) as fh:
            json.dump(doc, fh)
            path = fh.name
        try:
            self.assertEqual(main(["--format", "json", "ssp", path]), 0)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
