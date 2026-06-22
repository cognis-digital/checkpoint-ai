# Scenario 08 — Scoping controls out with not_applicable

## Where the data came from

**batch-ocr-digitizer** is plain OCR: it turns scanned forms into text that clerks
review before storage. Records Management argued that two controls genuinely do
not apply — **MAP-2** (foreseeable-misuse / impacted-populations analysis) and
**MEA-2** (disaggregated bias testing) — because the system makes no decisions
about people and produces no protected-attribute outputs. They marked those
`not_applicable` with a documented rationale.

## What to expect

- EU AI Act tier: **minimal**.
- The two `not_applicable` controls are **excluded from the denominator**, so they
  neither help nor hurt the score and are **never counted as gaps**.
- Every remaining applicable control is `implemented`/`verified`, so the posture
  lands in the **Optimized** band and `assess` exits **0**.

## Run it

```bash
checkpoint-ai assess demos/08-na-scoping/self-assessment.json
# confirm the two controls render as 'n/a' and are absent from the gap list:
checkpoint-ai --format json assess demos/08-na-scoping/self-assessment.json
```

## How to act

`not_applicable` is the correct tool for legitimately out-of-scope controls — but
each one needs a written justification in your assessment record. Use this demo to
show auditors that scoping decisions are explicit and do not silently inflate the
score.
