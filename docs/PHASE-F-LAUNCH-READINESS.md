# Phase F — Launch Readiness

This phase is the final launch gate. It is intentionally fail-closed.

## Required observable evidence

1. Approved model runtime is provisioned.
2. Local/self-hosted model health check passes.
3. Real coding-agent smoke test passes in an isolated workspace.
4. A second unrelated customer project completes end-to-end.
5. Vercel delivery for that second project is verified.
6. Customer package cost and quality are measured against the actual runtime.

## Gate

Run:

```bash
python scripts/phase_f_launch_gate.py --evidence launch-evidence.json
```

Every required field must be the boolean `true`. No deployment status, unit test, or simulated fixture may substitute for an environment-dependent evidence item.

## Operational completion

When all six evidence items are observed, record the evidence in the launch handoff and mark the product launch-ready. If any item is missing, the gate remains NOT_READY and no launch claim is made.
