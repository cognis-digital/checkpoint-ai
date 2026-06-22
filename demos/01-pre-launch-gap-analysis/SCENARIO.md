# Scenario 01 — Pre-launch gap analysis for a support copilot

## Where the data came from

The AI Platform team is six weeks out from launching **atlas-support-copilot**, an
external-facing support chatbot that drafts replies for human agents. A program
manager ran a workshop and recorded each control's honest implementation status
into `self-assessment.json`. Governance and human-oversight are in good shape,
but measurement (bias/robustness/accuracy) and data provenance are thin.

## What to expect

- EU AI Act tier: **limited** (chatbot + content generation — transparency duties only).
- Overall posture in the **Developing/Defined** band.
- Several open gaps, including the weight-5 controls **MAP-3** (data provenance)
  and **MEA-2** (bias testing) — so `assess` exits **non-zero (2)**, failing a CI gate.

## Run it

```bash
checkpoint-ai assess demos/01-pre-launch-gap-analysis/self-assessment.json
# machine-readable for a launch-readiness dashboard:
checkpoint-ai --format json assess demos/01-pre-launch-gap-analysis/self-assessment.json
# generate the remediation backlog (POA&M):
checkpoint-ai --format json ssp demos/01-pre-launch-gap-analysis/self-assessment.json
```

## How to act

Treat the high-priority POA&M items as launch blockers. The two weight-5 gaps
(data-provenance ledger and disaggregated bias testing) should be closed — or
formally risk-accepted by the accountability owner — before go-live.
