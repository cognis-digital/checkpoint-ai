"""CHECKPOINT-AI: NIST AI RMF / EU AI Act / ISO 42001 self-assessment & SSP generator.

Standard-library-only, zero-install governance engine in the spirit of usnistgov/OSCAL.
Scores an AI system against control catalogs, computes risk posture, and emits a
System Security Plan (SSP) skeleton with gap remediation.
"""
from .core import (
    CONTROL_CATALOG,
    FRAMEWORKS,
    Assessment,
    AssessmentResult,
    ControlResult,
    assess,
    classify_eu_risk_tier,
    generate_ssp,
    load_assessment,
)

TOOL_NAME = "CHECKPOINT-AI"
TOOL_VERSION = "1.0.0"

__all__ = [
    "TOOL_NAME",
    "TOOL_VERSION",
    "CONTROL_CATALOG",
    "FRAMEWORKS",
    "Assessment",
    "AssessmentResult",
    "ControlResult",
    "assess",
    "classify_eu_risk_tier",
    "generate_ssp",
    "load_assessment",
]
