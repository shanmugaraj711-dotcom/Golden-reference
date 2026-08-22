# Project Factory V3 — Customer Experience

## Customer journey
1. Intake: collect project goal, required pages/features, target audience, preferred stack, delivery model and destination ownership.
2. Plan: normalize requirements into a project brief and acceptance criteria.
3. Generate: run the guarded Project Factory generation pipeline.
4. Quality gate: validate structure, required assets, configuration safety and output manifest.
5. Preview: provide a reviewable preview before final delivery when the model requires approval.
6. Approval: record customer approval or requested changes.
7. Delivery: execute Transfer, Deploy, or Managed according to the authorized destination contract.
8. Verify: perform live health check and record deployment evidence.
9. Handoff: provide repository, live URL, ownership/access instructions, version and support information.
10. Maintain: for Managed customers, track changes, deployments, health and support obligations.

## Customer-facing states
INTAKE → PLANNING → GENERATING → REVIEW → APPROVED → DELIVERING → VERIFYING → LIVE → HANDED_OFF / MANAGED

Failure states: BLOCKED_AUTHORIZATION, GENERATION_FAILED, QUALITY_FAILED, DELIVERY_FAILED, HEALTHCHECK_FAILED.

## Rules
- Never deploy without an explicit destination authorization.
- Never expose provider credentials to customers or generated source.
- Never report LIVE without an observable health check.
- Keep customer projects isolated from PromptStudio production.
- Preserve a delivery manifest and evidence for every completed project.
