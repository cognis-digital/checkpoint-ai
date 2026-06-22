"""Command-line interface for CHECKPOINT-AI."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from . import TOOL_NAME, TOOL_VERSION
from .core import (
    CONTROL_CATALOG,
    AssessmentError,
    assess,
    generate_ssp,
    load_assessment,
    to_csv,
    to_sarif,
)


def _print_table(result) -> None:
    print(f"{TOOL_NAME} assessment: {result.system_name}")
    print(f"  owner            : {result.owner}")
    print(f"  EU AI Act tier   : {result.eu_risk_tier}")
    print(f"  overall posture  : {result.overall_score}/100 ({result.maturity})")
    print("  function scores  :")
    for func, score in sorted(result.function_scores.items()):
        print(f"    {func:<9}: {score}/100")
    print("  framework cover  :")
    for fw, pct in result.framework_coverage.items():
        print(f"    {fw:<12}: {pct}%")
    print("  controls         :")
    for c in result.controls:
        flag = "GAP " if c.gap else ("n/a " if not c.applicable else "ok  ")
        print(f"    [{flag}] {c.control_id:<6} {c.status:<13} {c.title}")
    if result.gaps:
        print(f"  open gaps        : {', '.join(result.gaps)}")


def _cmd_catalog(args) -> int:
    if args.format == "json":
        print(json.dumps(CONTROL_CATALOG, indent=2))
    else:
        print(f"{TOOL_NAME} control catalog ({len(CONTROL_CATALOG)} controls)")
        for c in CONTROL_CATALOG:
            fws = " ".join(f"{k}={v}" for k, v in c["frameworks"].items())
            print(f"  {c['id']:<6} (w{c['weight']}) {c['function']:<8} {c['title']}")
            print(f"         {fws}")
    return 0


def _cmd_assess(args) -> int:
    assessment = load_assessment(args.input)
    result = assess(assessment)
    if args.format == "json":
        print(json.dumps(result.to_dict(), indent=2))
    elif args.format == "sarif":
        print(json.dumps(to_sarif(result), indent=2))
    elif args.format == "csv":
        sys.stdout.write(to_csv(result))
    else:
        _print_table(result)
    # Non-zero exit when high-priority (weight>=5) gaps remain unaddressed.
    high_gaps = [c for c in result.controls if c.gap and c.weight >= 5]
    return 2 if high_gaps else 0


def _cmd_ssp(args) -> int:
    assessment = load_assessment(args.input)
    result = assess(assessment)
    ssp = generate_ssp(result, purpose=assessment.purpose)
    if args.format == "json":
        print(json.dumps(ssp, indent=2))
    else:
        meta = ssp["metadata"]
        sc = ssp["system_characteristics"]
        print(meta["title"])
        print(f"  owner       : {meta['system_owner']}")
        print(f"  generated   : {meta['generated_utc']}")
        print(f"  risk tier   : {sc['eu_ai_act_risk_tier']}")
        print(f"  posture     : {sc['overall_posture_score']}/100 ({sc['maturity_level']})")
        poam = ssp["plan_of_action_and_milestones"]
        print(f"  POA&M items : {len(poam)}")
        for item in poam:
            print(f"    [{item['priority']:<6}] {item['control_id']}: {item['remediation']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="checkpoint-ai",
        description=f"{TOOL_NAME}: NIST AI RMF / EU AI Act / ISO 42001 self-assessment & SSP generator.",
    )
    parser.add_argument("--version", action="version", version=f"{TOOL_NAME} {TOOL_VERSION}")
    parser.add_argument(
        "--format",
        choices=["table", "json", "sarif", "csv"],
        default="table",
        help="output format (sarif/csv apply to the 'assess' command)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_cat = sub.add_parser("catalog", help="list the cross-walked control catalog")
    p_cat.set_defaults(func=_cmd_catalog)

    p_assess = sub.add_parser("assess", help="score a self-assessment JSON file")
    p_assess.add_argument("input", help="path to assessment JSON")
    p_assess.set_defaults(func=_cmd_assess)

    p_ssp = sub.add_parser("ssp", help="generate an OSCAL-flavored SSP from an assessment")
    p_ssp.add_argument("input", help="path to assessment JSON")
    p_ssp.set_defaults(func=_cmd_ssp)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except AssessmentError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
