# Scenario 10 — Third-party model intake / vendor risk

## Where the data came from

**thirdparty-summarizer-saas** is a vendor SaaS that summarizes internal
documents. Procurement does **not** control the training data or model internals,
so the assessment reflects a mix of vendor attestations and the wrapper controls
the buying org actually owns. The hardest gaps are exactly the ones that depend on
the vendor: **MAP-3** (data provenance) and **MEA-2** (bias testing) are
`not_started` because the vendor has not provided evidence.

## What to expect

- EU AI Act tier: **limited** (content generation).
- Overall posture in the **Developing/Defined** band.
- Multiple gaps including weight-5 **MAP-3** and **MEA-2**, so `assess` exits
  **non-zero (2)**. These are the items to push back to the vendor in a
  due-diligence questionnaire.

## Run it

```bash
checkpoint-ai assess demos/10-vendor-model-intake/self-assessment.json
# hand the gap list to procurement as a spreadsheet:
checkpoint-ai --format csv assess demos/10-vendor-model-intake/self-assessment.json > vendor-gaps.csv
```

## How to act

Convert the open weight-5 gaps into contractual asks: require the vendor to supply
a data-provenance statement (MAP-3) and disaggregated bias-test results (MEA-2)
before sign-off. Re-run after the vendor responds; controls you genuinely cannot
inherit and that do not apply can be marked `not_applicable` with justification.
