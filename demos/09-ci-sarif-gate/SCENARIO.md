# Scenario 09 — Wiring the gap check into CI with SARIF

## Where the data came from

**loanflow-adjudicator** recommends approve/decline on consumer credit for a human
underwriter. Credit-for-essential-services is an **Annex III high-risk** use case,
so MLOps wants every governance change to fail the build until the posture is
clean. This demo shows the CI pattern: exit-code gate + SARIF upload so each open
gap shows up as an annotation in the code-scanning dashboard.

## What to expect

- EU AI Act tier: **high** (essential services).
- One open gap: **MEA-2** (bias testing, weight 5) — `assess` exits **non-zero (2)**,
  which fails the CI step.
- `--format sarif` emits a valid SARIF 2.1.0 log with **one rule per control** and
  **one result per gap** (here, a single result for MEA-2), each carrying a
  `security-severity` and the NIST / EU AI Act / ISO 42001 crosswalk.

## Run it

```bash
# fail the build on a weight-5 gap:
checkpoint-ai assess demos/09-ci-sarif-gate/self-assessment.json; echo "exit=$?"

# and publish the findings to a code-scanning dashboard:
checkpoint-ai --format sarif assess demos/09-ci-sarif-gate/self-assessment.json > checkpoint.sarif.json
```

### GitHub Actions sketch

```yaml
- name: AI governance gate
  run: checkpoint-ai assess assessment.json   # non-zero exit fails the job
- name: Emit SARIF (always)
  if: always()
  run: checkpoint-ai --format sarif assess assessment.json > checkpoint.sarif.json
- uses: github/codeql-action/upload-sarif@v3
  if: always()
  with:
    sarif_file: checkpoint.sarif.json
```

## How to act

The build stays red until MEA-2 reaches `implemented`. Reviewers see the gap as a
SARIF annotation tagged with `framework:eu_ai_act = Art.10`, giving them the exact
clause to remediate against — no context-switching out of the dev workflow.
