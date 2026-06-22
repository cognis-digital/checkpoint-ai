# Scenario 04 — Prohibited practice: the tier check that stops a project

## Where the data came from

A strategy office floated **civic-trust-score**, a proposal to assign citizens a
general-purpose "trustworthiness" score from unrelated behavioral data and gate
access to services on it. On paper the team filled out a *perfect* control
posture — every control `verified`. This demo exists to show that **strong
control hygiene does not rescue a prohibited use case.**

## What to expect

- EU AI Act tier: **unacceptable** (social scoring + real-time remote biometric
  identification are Art.5 prohibited practices).
- Overall posture: **100/100 (Optimized)**, **zero gaps** — so `assess` exits **0**.
- The signal that matters is the **risk tier**, not the score. A reviewer reading
  the table or JSON sees `unacceptable` and stops the project regardless of the
  green posture.

## Run it

```bash
checkpoint-ai assess demos/04-prohibited-practice-stop/self-assessment.json
checkpoint-ai --format json assess demos/04-prohibited-practice-stop/self-assessment.json
```

## How to act

`eu_ai_act_risk_tier: unacceptable` is a hard stop. No amount of governance
makes a prohibited practice deployable in the EU. Escalate to legal, kill or
fundamentally redesign the use case. This demo is a reminder to gate on the tier
field — not just the exit code — in any automated review.
