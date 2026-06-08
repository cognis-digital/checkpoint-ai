# Demo 01 - Basic: Loan-approval ML model assessment

## Scenario

`creditflow-scoring` is an internal+external machine-learning model that scores
consumer loan applications. Because it is used for **employment/essential-services
style eligibility decisions on natural persons**, it falls under the EU AI Act's
**high-risk** tier (Annex III), so the bar for governance evidence is high.

The team has done some governance work (a policy owner exists, purpose is
documented, decisions are logged) but has **not** completed bias testing, human
oversight controls, or incident response, all of which are weight-5 controls.

## Run it

```bash
# See the catalog
python -m checkpoint_ai --format table catalog

# Score the assessment (exits non-zero because high-weight gaps remain)
python -m checkpoint_ai --format json assess demos/01-basic/assessment.json

# Generate the System Security Plan with a prioritized POA&M
python -m checkpoint_ai --format json ssp demos/01-basic/assessment.json
```

## Expected outcome

- **EU risk tier:** `high` (driven by `employment_screening` use case).
- **Overall posture:** mid-range (`Developing`/`Defined` maturity).
- **`assess` exit code:** `2`, because weight-5 controls `MEA-2` (bias testing)
  and `MAN-1` (human oversight) are still gaps. This makes the tool usable as a
  CI gate that blocks deployment until high-impact controls are closed.
- **SSP POA&M:** lists the open gaps with high-priority items first and concrete
  remediation steps, cross-walked to NIST / EU AI Act / ISO 42001 clauses.
