# Scenario 07 — Greenfield baseline: the day-zero assessment

## Where the data came from

**newproject-llm-assistant** is a brand-new generative-AI project. Nobody has
done any governance work yet — every control is `not_started` and the owner is
`unassigned`. This is the honest day-zero baseline you run to produce the
initial backlog.

## What to expect

- EU AI Act tier: **limited** (content generation — transparency duties).
- Overall posture: **0/100 (Initial)**.
- **All 12 controls are open gaps**; because several are weight-5, `assess`
  exits **non-zero (2)**.
- The generated SSP's POA&M lists every control, **high-priority items first** —
  a ready-made governance plan for a new system.

## Run it

```bash
checkpoint-ai assess demos/07-greenfield-baseline/self-assessment.json
# turn the empty posture into a prioritized work plan:
checkpoint-ai --format json ssp demos/07-greenfield-baseline/self-assessment.json
```

## How to act

Start at the top of the POA&M: assign the accountability owner (GOV-1), then work
down the weight-5 controls (data provenance, bias testing, human oversight). Re-run
after each milestone and watch the posture climb out of `Initial`.
