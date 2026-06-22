# Scenario 02 — Near-complete ISO/IEC 42001 readiness

## Where the data came from

**helios-demand-forecaster** is an internal energy-demand model whose AI
Management System (AIMS) is being prepared for an ISO/IEC 42001 stage-1 audit.
The program office has driven nearly every control to `implemented` or
`verified`. One control — **MEA-2** (disaggregated bias/fairness testing) — is
still `partial` while the team finishes a subgroup evaluation.

## What to expect

- EU AI Act tier: **limited** (internal recommendation aid with human review).
- Overall posture in the **Managed/Optimized** band (high 80s / low 90s).
- Exactly **one open gap: MEA-2** (weight 5) — so `assess` exits **non-zero (2)**.
  Once MEA-2 reaches `implemented`, the assessment is clean and the AIMS is
  audit-ready.

## Run it

```bash
checkpoint-ai assess demos/02-iso-42001-readiness/self-assessment.json
# framework-by-framework coverage for the audit pack:
checkpoint-ai --format json assess demos/02-iso-42001-readiness/self-assessment.json
```

## How to act

The single remaining gap is the last item on the stage-1 punch list. Close MEA-2
(or attach the in-flight evidence), re-run, confirm a clean exit, then export the
SSP as the AIMS documentation artifact.
