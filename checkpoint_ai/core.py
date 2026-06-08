"""CHECKPOINT-AI — AI compliance self-assessment scorer."""
from __future__ import annotations
import json, time
from pathlib import Path
from cognis_core import Finding, ScanResult, score

TOOL_NAME = "CHECKPOINT-AI"
TOOL_VERSION = "0.1.0"

# Control families: NIST AI RMF (GOVERN/MAP/MEASURE/MANAGE), EU AI Act, ISO 42001
CONTROLS = [
    ("CP-GOV-1.1", "high",   2.5, "AI risk management policy documented"),
    ("CP-GOV-1.2", "high",   2.5, "Roles and responsibilities defined"),
    ("CP-MAP-2.1", "high",   2.5, "AI system context characterized"),
    ("CP-MAP-2.2", "medium", 2.0, "Intended use and users documented"),
    ("CP-MEAS-3.1","high",   2.5, "Testing/evaluation plan in place"),
    ("CP-MEAS-3.2","high",   2.5, "Bias and fairness metrics defined"),
    ("CP-MGMT-4.1","critical",3.0,"Incident response plan for AI failures"),
    ("CP-MGMT-4.2","high",   2.5, "Continuous monitoring and post-market surveillance"),
    ("CP-EUAI-IX", "critical",3.0,"High-risk Annex III system: conformity assessment recorded"),
]

def scan(target: str, **opts) -> ScanResult:
    t0 = time.time()
    result = ScanResult(tool_name=TOOL_NAME, tool_version=TOOL_VERSION, target=str(target))
    p = Path(target)
    answers = {}
    if p.is_file():
        try:
            answers = json.loads(p.read_text())
        except Exception:
            pass
    result.items_scanned = len(CONTROLS)
    for cid, sev, w, desc in CONTROLS:
        status = (answers.get(cid) or "").lower()
        if status not in ("yes","implemented","compliant"):
            result.add(Finding(
                id=cid, severity=sev, weight=w, title=f"MISSING_CONTROL_{cid}",
                description=f"{desc} (current: {status or 'unanswered'})",
                location=str(target),
                remediation=f"Implement and document control {cid}. See NIST AI RMF + ISO/IEC 42001.",
                category="ai-compliance",
            ))
    result.composite_score, result.risk_level = score(result.findings)
    result.scan_duration_ms = int((time.time()-t0)*1000)
    return result
