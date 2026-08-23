# Phase E — Real E2E Batch

## Scope
This batch turns the existing V3 E2E contract into an executable production acceptance gate without fabricating deployment evidence.

### Included
- Read-only production API smoke check.
- Persisted Firestore project read/shape check.
- Customer Delivery dashboard marker check.
- Transfer / Deploy / Managed delivery-plan contract checks.
- Regression tests for the complete acceptance runner.

## Production execution
Run:

```bash
python scripts/phase_e_e2e.py --base-url https://golden-reference.vercel.app
```

For a specific persisted project:

```bash
python scripts/phase_e_e2e.py --base-url https://golden-reference.vercel.app --project-id <PROJECT_ID>
```

## Evidence boundary
A PASS from this runner proves the live Project Factory surface and delivery-model contract. It does **not** claim Deploy or Managed completion by unit test alone.

The remaining real-E2E evidence must use a fresh destination:

- Transfer → destination repository + handoff evidence → `HANDED_OFF`
- Deploy → destination repository + hosting target + deployment URL + external health check → `LIVE`
- Managed → version-1 evidence preserved + change request + version-2 deployment + external health check → `MANAGED`

Those terminal states are the acceptance criteria from `docs/V3_E2E_RUNBOOK.md`.

## Completion rule
Phase E is complete only when the required delivery-model run has observable destination/deployment/health evidence, the dashboard reads that persisted evidence, and the final evidence record is retained. The runner intentionally fails closed rather than inventing evidence.
