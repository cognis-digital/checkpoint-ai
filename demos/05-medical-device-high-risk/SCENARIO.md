# Scenario 05 — High-risk medical device that passes the gate

## Where the data came from

**retinascan-triage** flags retinal images suggestive of diabetic retinopathy to
prioritize ophthalmologist review (decision support; a clinician diagnoses).
Medical devices are **Annex III high-risk**, so Quality & Regulatory Affairs held
the system to a high bar before submitting it for review. Every applicable
control is `implemented` or `verified`.

## What to expect

- EU AI Act tier: **high** (medical device).
- Overall posture in the **Optimized** band (90+).
- **Zero open gaps** — `assess` exits **0**. This is the "good day" reference:
  a high-risk system that nonetheless passes a CI gate because the posture is
  genuinely complete.

## Run it

```bash
checkpoint-ai assess demos/05-medical-device-high-risk/self-assessment.json && echo "gate passed (exit 0)"
checkpoint-ai --format json ssp demos/05-medical-device-high-risk/self-assessment.json
```

## How to act

Use this as the target state for a high-risk system: tier `high` *and* a clean
gap list. The SSP export here has an empty POA&M, which is exactly what you want
to attach to a technical-documentation file under EU AI Act Art.11.
