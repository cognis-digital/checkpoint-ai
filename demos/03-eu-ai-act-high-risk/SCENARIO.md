# Scenario 03 — EU AI Act high-risk: hiring system conformity prep

## Where the data came from

**sentinel-resume-screener** ranks job applicants for recruiter review.
Employment screening is an **Annex III high-risk** use case under the EU AI Act,
and the declared use cases also include biometric identification. The Responsible
AI Office captured the current control posture ahead of a conformity assessment.
Governance is solid, but the bias-testing control (**MEA-2**) is only `planned`
and several measurement/management controls are `partial`.

## What to expect

- EU AI Act tier: **high** (employment screening / biometric ID — Annex III).
- Overall posture in the **Defined/Managed** band.
- Open gaps including the weight-5 **MEA-2** (bias testing) — `assess` exits
  **non-zero (2)**. For a high-risk system, an open bias-testing gap is the kind
  of finding that blocks a CE-marking conformity declaration.

## Run it

```bash
checkpoint-ai assess demos/03-eu-ai-act-high-risk/self-assessment.json
# emit SARIF so the gap lands in a code-scanning / GRC dashboard:
checkpoint-ai --format sarif assess demos/03-eu-ai-act-high-risk/self-assessment.json > sentinel.sarif.json
```

## How to act

For a high-risk system, prioritize the bias/fairness and data-provenance gaps —
they map directly to EU AI Act Art.10 and Art.15. Use the SARIF output to track
each gap to closure in your existing security-dashboard workflow, then re-run
before signing the declaration of conformity.
