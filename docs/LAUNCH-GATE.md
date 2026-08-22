# Launch Gate

## Ready in repository

- Factory engine and bounded repair loop implemented.
- Deterministic fixture gates implemented.
- Project and coding-agent adapters implemented.
- Model provider/router abstraction implemented.
- Local/self-hosted provider implemented.
- Zero-cost policy is fail-closed by default.
- GitHub CI test gate configured.
- Customer flow, quality gates, economics and architecture documented.

## Environment-dependent before real customer launch

- Approved model runtime is provisioned.
- Local model health check passes.
- Real coding-agent smoke test passes in an isolated workspace.
- Second unrelated project is built end-to-end.
- Vercel delivery is verified for that project.
- Customer package is tested against the actual cost and quality measurements.

No item in the environment-dependent section should be marked complete without observable evidence.
