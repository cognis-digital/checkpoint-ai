"""Core engine for CHECKPOINT-AI.

Implements a real control-scoring model mapping a system self-assessment onto a
cross-walked catalog of NIST AI RMF (GOVERN/MAP/MEASURE/MANAGE), EU AI Act, and
ISO/IEC 42001 controls. No stubs: scoring, weighting, gap analysis, EU risk-tier
classification, and SSP generation are all fully computed.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List

TOOL_NAME: str = "CHECKPOINT-AI"
TOOL_VERSION: str = "0.1.0"

# Implementation status -> normalized score in [0.0, 1.0].
IMPLEMENTATION_LEVELS: Dict[str, float] = {
    "not_started": 0.0,
    "planned": 0.25,
    "partial": 0.5,
    "implemented": 0.85,
    "verified": 1.0,
    "not_applicable": -1.0,  # sentinel: excluded from scoring
}

# Cross-walked control catalog. Each control carries a weight (impact on posture)
# and the framework clauses it satisfies. Weights are integers 1..5.
CONTROL_CATALOG: List[Dict[str, Any]] = [
    {
        "id": "GOV-1",
        "function": "GOVERN",
        "title": "AI governance policy & accountability owner",
        "weight": 5,
        "frameworks": {"nist_ai_rmf": "GOVERN 1.1", "eu_ai_act": "Art.17", "iso_42001": "5.2"},
    },
    {
        "id": "GOV-2",
        "function": "GOVERN",
        "title": "Risk tolerance & escalation thresholds defined",
        "weight": 4,
        "frameworks": {"nist_ai_rmf": "GOVERN 1.3", "eu_ai_act": "Art.9", "iso_42001": "6.1"},
    },
    {
        "id": "GOV-3",
        "function": "GOVERN",
        "title": "Workforce AI competency & training",
        "weight": 3,
        "frameworks": {"nist_ai_rmf": "GOVERN 2.2", "eu_ai_act": "Art.4", "iso_42001": "7.2"},
    },
    {
        "id": "MAP-1",
        "function": "MAP",
        "title": "Intended purpose & context of use documented",
        "weight": 4,
        "frameworks": {"nist_ai_rmf": "MAP 1.1", "eu_ai_act": "Art.11", "iso_42001": "8.1"},
    },
    {
        "id": "MAP-2",
        "function": "MAP",
        "title": "Foreseeable misuse & impacted populations identified",
        "weight": 4,
        "frameworks": {"nist_ai_rmf": "MAP 3.1", "eu_ai_act": "Art.9", "iso_42001": "6.1.2"},
    },
    {
        "id": "MAP-3",
        "function": "MAP",
        "title": "Data provenance & lawful basis recorded",
        "weight": 5,
        "frameworks": {"nist_ai_rmf": "MAP 2.3", "eu_ai_act": "Art.10", "iso_42001": "7.4"},
    },
    {
        "id": "MEA-1",
        "function": "MEASURE",
        "title": "Performance & accuracy metrics evaluated",
        "weight": 4,
        "frameworks": {"nist_ai_rmf": "MEASURE 2.3", "eu_ai_act": "Art.15", "iso_42001": "9.1"},
    },
    {
        "id": "MEA-2",
        "function": "MEASURE",
        "title": "Bias / fairness testing across subgroups",
        "weight": 5,
        "frameworks": {"nist_ai_rmf": "MEASURE 2.11", "eu_ai_act": "Art.10", "iso_42001": "9.1"},
    },
    {
        "id": "MEA-3",
        "function": "MEASURE",
        "title": "Adversarial robustness & security testing",
        "weight": 4,
        "frameworks": {"nist_ai_rmf": "MEASURE 2.7", "eu_ai_act": "Art.15", "iso_42001": "8.3"},
    },
    {
        "id": "MAN-1",
        "function": "MANAGE",
        "title": "Human oversight & intervention controls",
        "weight": 5,
        "frameworks": {"nist_ai_rmf": "MANAGE 1.1", "eu_ai_act": "Art.14", "iso_42001": "8.4"},
    },
    {
        "id": "MAN-2",
        "function": "MANAGE",
        "title": "Incident response & post-market monitoring",
        "weight": 4,
        "frameworks": {"nist_ai_rmf": "MANAGE 4.1", "eu_ai_act": "Art.72", "iso_42001": "10.1"},
    },
    {
        "id": "MAN-3",
        "function": "MANAGE",
        "title": "Logging & traceability of system decisions",
        "weight": 4,
        "frameworks": {"nist_ai_rmf": "MANAGE 2.2", "eu_ai_act": "Art.12", "iso_42001": "8.5"},
    },
]

FRAMEWORKS: Dict[str, str] = {
    "nist_ai_rmf": "NIST AI Risk Management Framework 1.0",
    "eu_ai_act": "EU Artificial Intelligence Act (Reg. 2024/1689)",
    "iso_42001": "ISO/IEC 42001:2023",
}

_CATALOG_BY_ID = {c["id"]: c for c in CONTROL_CATALOG}

# EU AI Act risk tiers ordered by severity.
_EU_TIERS = ["minimal", "limited", "high", "unacceptable"]


class AssessmentError(ValueError):
    """Raised when an assessment document is invalid."""


@dataclass
class Assessment:
    """Parsed self-assessment input for one AI system."""

    system_name: str
    owner: str
    purpose: str
    deployment_context: str = "internal"
    eu_use_cases: List[str] = field(default_factory=list)
    responses: Dict[str, str] = field(default_factory=dict)


@dataclass
class ControlResult:
    control_id: str
    function: str
    title: str
    weight: int
    status: str
    score: float  # weighted contribution (0..weight); -1 if N/A
    applicable: bool
    frameworks: Dict[str, str]
    gap: bool


@dataclass
class AssessmentResult:
    system_name: str
    owner: str
    generated_utc: str
    eu_risk_tier: str
    overall_score: float  # 0..100
    maturity: str
    function_scores: Dict[str, float]
    framework_coverage: Dict[str, float]
    controls: List[ControlResult]
    gaps: List[str]

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d


def classify_eu_risk_tier(eu_use_cases: List[str], deployment_context: str) -> str:
    """Classify the EU AI Act risk tier from declared use cases.

    Real (simplified) Annex III / Art.5 mapping. Returns highest applicable tier.
    """
    if not isinstance(eu_use_cases, list):
        eu_use_cases = []
    unacceptable = {"social_scoring", "manipulation", "realtime_biometric_id", "emotion_workplace"}
    high = {
        "biometric_id",
        "critical_infrastructure",
        "education_scoring",
        "employment_screening",
        "essential_services",
        "law_enforcement",
        "migration_border",
        "justice",
        "medical_device",
    }
    limited = {"chatbot", "content_generation", "deepfake", "recommendation"}

    cases = {c.strip().lower() for c in eu_use_cases}
    if cases & unacceptable:
        return "unacceptable"
    if cases & high:
        return "high"
    if cases & limited:
        return "limited"
    return "minimal"


def _maturity_label(score: float) -> str:
    if score >= 90:
        return "Optimized"
    if score >= 75:
        return "Managed"
    if score >= 50:
        return "Defined"
    if score >= 25:
        return "Developing"
    return "Initial"


def assess(assessment: Assessment) -> AssessmentResult:
    """Score an assessment against the catalog and compute posture."""
    if not assessment.system_name or not str(assessment.system_name).strip():
        raise AssessmentError("system_name is required and must not be blank")

    controls: List[ControlResult] = []
    func_weighted: Dict[str, float] = {}
    func_max: Dict[str, float] = {}
    fw_satisfied: Dict[str, float] = {k: 0.0 for k in FRAMEWORKS}
    fw_total: Dict[str, float] = {k: 0.0 for k in FRAMEWORKS}
    gaps: List[str] = []

    total_weighted = 0.0
    total_max = 0.0

    for ctrl in CONTROL_CATALOG:
        cid = ctrl["id"]
        status = assessment.responses.get(cid, "not_started")
        if status not in IMPLEMENTATION_LEVELS:
            raise AssessmentError(
                f"control {cid}: unknown status '{status}' "
                f"(expected one of {sorted(IMPLEMENTATION_LEVELS)})"
            )
        level = IMPLEMENTATION_LEVELS[status]
        weight = ctrl["weight"]
        applicable = level >= 0.0
        func = ctrl["function"]

        if applicable:
            contribution = level * weight
            total_weighted += contribution
            total_max += weight
            func_weighted[func] = func_weighted.get(func, 0.0) + contribution
            func_max[func] = func_max.get(func, 0.0) + weight
            for fw in ctrl["frameworks"]:
                fw_total[fw] += 1.0
                # A framework clause counts as covered if implemented or better.
                if level >= IMPLEMENTATION_LEVELS["implemented"]:
                    fw_satisfied[fw] += 1.0
            score_val = round(contribution, 3)
        else:
            score_val = -1.0

        # A gap is an applicable control below 'implemented'.
        is_gap = applicable and level < IMPLEMENTATION_LEVELS["implemented"]
        if is_gap:
            gaps.append(cid)

        controls.append(
            ControlResult(
                control_id=cid,
                function=func,
                title=ctrl["title"],
                weight=weight,
                status=status,
                score=score_val,
                applicable=applicable,
                frameworks=dict(ctrl["frameworks"]),
                gap=is_gap,
            )
        )

    overall = round(100.0 * total_weighted / total_max, 1) if total_max else 0.0
    function_scores = {
        f: round(100.0 * func_weighted.get(f, 0.0) / func_max[f], 1)
        for f in func_max
    }
    framework_coverage = {
        fw: round(100.0 * fw_satisfied[fw] / fw_total[fw], 1) if fw_total[fw] else 0.0
        for fw in FRAMEWORKS
    }

    return AssessmentResult(
        system_name=assessment.system_name,
        owner=assessment.owner,
        generated_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        eu_risk_tier=classify_eu_risk_tier(assessment.eu_use_cases, assessment.deployment_context),
        overall_score=overall,
        maturity=_maturity_label(overall),
        function_scores=function_scores,
        framework_coverage=framework_coverage,
        controls=controls,
        gaps=gaps,
    )


def load_assessment(path: str) -> Assessment:
    """Load and validate an assessment JSON file."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError as exc:
        raise AssessmentError(f"assessment file not found: {path}") from exc
    except IsADirectoryError as exc:
        raise AssessmentError(f"path is a directory, not a file: {path}") from exc
    except PermissionError as exc:
        raise AssessmentError(f"permission denied reading: {path}") from exc
    except OSError as exc:
        raise AssessmentError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise AssessmentError(f"invalid JSON in {path}: {exc}") from exc
    return load_assessment_dict(data)


def load_assessment_dict(data: Dict[str, Any]) -> Assessment:
    if not isinstance(data, dict):
        raise AssessmentError("assessment must be a JSON object")
    if "system_name" not in data:
        raise AssessmentError("assessment missing required field 'system_name'")
    system_name = data["system_name"]
    if not isinstance(system_name, (str, int, float)) or not str(system_name).strip():
        raise AssessmentError("'system_name' must be a non-empty string")
    responses = data.get("responses", {})
    if not isinstance(responses, dict):
        raise AssessmentError("'responses' must be an object of control_id -> status")
    eu_use_cases_raw = data.get("eu_use_cases", [])
    if not isinstance(eu_use_cases_raw, list):
        raise AssessmentError("'eu_use_cases' must be a list")
    for i, uc in enumerate(eu_use_cases_raw):
        if not isinstance(uc, str):
            raise AssessmentError(
                f"'eu_use_cases[{i}]' must be a string, got {type(uc).__name__}"
            )
    unknown = set(responses) - set(_CATALOG_BY_ID)
    if unknown:
        raise AssessmentError(f"unknown control id(s): {sorted(unknown)}")
    return Assessment(
        system_name=str(system_name).strip(),
        owner=str(data.get("owner", "unassigned")),
        purpose=str(data.get("purpose", "")),
        deployment_context=str(data.get("deployment_context", "internal")),
        eu_use_cases=[str(uc) for uc in eu_use_cases_raw],
        responses={str(k): str(v) for k, v in responses.items()},
    )


_REMEDIATION = {
    "GOV-1": "Appoint a named AI accountability owner and ratify a governance policy.",
    "GOV-2": "Document quantitative risk tolerance bands and escalation triggers.",
    "GOV-3": "Stand up role-based AI literacy training with completion tracking.",
    "MAP-1": "Write an intended-purpose statement and operational context register.",
    "MAP-2": "Run a structured misuse/abuse workshop; log impacted populations.",
    "MAP-3": "Build a data provenance ledger with lawful-basis attestations.",
    "MEA-1": "Define accuracy/performance KPIs and schedule recurring evaluation.",
    "MEA-2": "Execute disaggregated bias testing across protected subgroups.",
    "MEA-3": "Commission adversarial robustness and red-team security testing.",
    "MAN-1": "Implement human-in-the-loop override and stop controls.",
    "MAN-2": "Establish incident response runbook and post-market monitoring.",
    "MAN-3": "Enable immutable decision logging with retention policy.",
}


def generate_ssp(result: AssessmentResult, purpose: str = "") -> Dict[str, Any]:
    """Produce an OSCAL-flavored System Security Plan skeleton from a result."""
    implemented = [c for c in result.controls if c.applicable and not c.gap]
    plan_items = []
    for cid in result.gaps:
        ctrl = _CATALOG_BY_ID.get(cid)
        if ctrl is None:  # defensive: gaps should always reference catalog entries
            continue
        plan_items.append(
            {
                "control_id": cid,
                "title": ctrl["title"],
                "priority": "high" if ctrl["weight"] >= 5 else "medium",
                "remediation": _REMEDIATION.get(cid, "Define and implement this control."),
                "satisfies": ctrl["frameworks"],
            }
        )
    # High-weight gaps first.
    plan_items.sort(key=lambda p: 0 if p["priority"] == "high" else 1)

    return {
        "oscal_flavor": "system-security-plan",
        "metadata": {
            "title": f"System Security Plan: {result.system_name}",
            "system_owner": result.owner,
            "generated_utc": result.generated_utc,
            "purpose": purpose,
        },
        "system_characteristics": {
            "eu_ai_act_risk_tier": result.eu_risk_tier,
            "overall_posture_score": result.overall_score,
            "maturity_level": result.maturity,
            "frameworks": FRAMEWORKS,
        },
        "control_implementation": {
            "implemented_count": len(implemented),
            "gap_count": len(result.gaps),
            "implemented_controls": [c.control_id for c in implemented],
            "framework_coverage_pct": result.framework_coverage,
        },
        "plan_of_action_and_milestones": plan_items,
    }
