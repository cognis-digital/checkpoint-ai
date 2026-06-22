"""Every shipped demo must load, assess, and export cleanly. No network."""
import glob
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from checkpoint_ai.core import (  # noqa: E402
    assess,
    load_assessment,
    to_csv,
    to_sarif,
)

DEMO_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "demos"
)

# Expected EU AI Act tier per demo directory — anchors the realistic scenarios.
EXPECTED_TIER = {
    "01-basic": "high",
    "01-pre-launch-gap-analysis": "limited",
    "02-iso-42001-readiness": "limited",
    "03-eu-ai-act-high-risk": "high",
    "04-prohibited-practice-stop": "unacceptable",
    "05-medical-device-high-risk": "high",
    "06-internal-analytics-minimal": "minimal",
    "07-greenfield-baseline": "limited",
    "08-na-scoping": "minimal",
    "09-ci-sarif-gate": "high",
    "10-vendor-model-intake": "limited",
}


def _demo_inputs():
    out = []
    for d in sorted(glob.glob(os.path.join(DEMO_DIR, "*"))):
        if not os.path.isdir(d):
            continue
        files = glob.glob(os.path.join(d, "*.json"))
        if files:
            out.append((os.path.basename(d), files[0]))
    return out


class TestDemos(unittest.TestCase):
    def test_demos_exist(self):
        self.assertGreaterEqual(len(_demo_inputs()), 10)

    def test_every_demo_assesses_and_exports(self):
        for name, path in _demo_inputs():
            with self.subTest(demo=name):
                a = load_assessment(path)
                r = assess(a)
                # tier matches the documented scenario
                if name in EXPECTED_TIER:
                    self.assertEqual(r.eu_risk_tier, EXPECTED_TIER[name])
                # exports never raise and stay JSON/CSV-shaped
                s = to_sarif(r)
                self.assertEqual(s["version"], "2.1.0")
                self.assertEqual(
                    {res["ruleId"] for res in s["runs"][0]["results"]}, set(r.gaps)
                )
                csv_text = to_csv(r)
                self.assertTrue(csv_text.startswith("control_id,"))

    def test_every_demo_has_scenario(self):
        for d in sorted(glob.glob(os.path.join(DEMO_DIR, "*"))):
            if not os.path.isdir(d):
                continue
            if glob.glob(os.path.join(d, "*.json")):
                self.assertTrue(
                    os.path.exists(os.path.join(d, "SCENARIO.md")),
                    f"{os.path.basename(d)} missing SCENARIO.md",
                )

    def test_clean_demos_have_no_weight5_gap(self):
        # Demos documented to exit 0 must carry no weight-5 gap.
        clean = {
            "04-prohibited-practice-stop",
            "05-medical-device-high-risk",
            "06-internal-analytics-minimal",
            "08-na-scoping",
        }
        for name, path in _demo_inputs():
            if name not in clean:
                continue
            with self.subTest(demo=name):
                r = assess(load_assessment(path))
                w5 = [c.control_id for c in r.controls if c.gap and c.weight >= 5]
                self.assertEqual(w5, [], f"{name} should have no weight-5 gap")


if __name__ == "__main__":
    unittest.main(verbosity=2)
