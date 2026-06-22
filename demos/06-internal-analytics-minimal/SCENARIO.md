# Scenario 06 — Minimal-risk internal tool: right-sizing the effort

## Where the data came from

**ledger-anomaly-flagger** is an internal analytics tool that surfaces unusual
journal entries for an accountant to investigate. It has no external exposure and
takes no automated decisions, so it declares **no EU use cases**. The finance data
team filled out the assessment to confirm they aren't over- or under-investing in
governance for a low-stakes system.

## What to expect

- EU AI Act tier: **minimal** (no Annex III / Art.5 use case declared).
- Overall posture in the **Defined** band.
- Open gaps exist, but **none are weight-5**, so `assess` exits **0** — the tool
  is signalling "improve when convenient, not a blocker."

## Run it

```bash
checkpoint-ai assess demos/06-internal-analytics-minimal/self-assessment.json; echo "exit=$?"
checkpoint-ai --format csv assess demos/06-internal-analytics-minimal/self-assessment.json
```

## How to act

For a minimal-risk system the exit code stays 0 even with gaps — that's the
intended behaviour. Pull the CSV into your control tracker and schedule the
lower-weight gaps (GOV-3 training, MEA-3 robustness) as routine improvements
rather than launch blockers.
