# Autonomous Customer Factory

## Product contract

A customer submits one project request. The Factory executes a configurable workflow and produces a deliverable. The workflow is persistent and independent of any chat/session.

### Canonical 10-step workflow

1. Intake
2. Requirements
3. Plan
4. Build
5. Test
6. Repair
7. Quality
8. Package
9. Deploy
10. Deliver

The implementation stores a version for every customer-requested revision. Customer feedback creates a new version and can start at any selected step, preserving the previous version as history.

## Founder/Admin control

Admin can:

- Start the full workflow: `1 → 10`.
- Start a bounded run such as `1 → 5`.
- Resume a paused run.
- Pause a run with a reason.
- Approve a version.
- Start a targeted revision from any stage, such as `4 → 10`.
- Select an output target such as `web`, `android`, `ios`, or another provider adapter.

The UI must expose these as explicit controls, while the worker remains the execution authority.

## Automation contract

A stage may checkpoint success only after observable evidence exists. Provider/API failures move the run into retry/fallback handling; they do not silently advance the stage. A blocked run remains resumable from its persisted checkpoint.

## Versioning contract

`V1` is immutable after delivery. A customer request such as “change the dashboard” produces `V2`, with the selected start stage and the original version retained. This makes targeted customer changes cheaper and auditable.

## Session independence

ChatGPT is only an operator/interface when used. It is not the runtime. The persistent run state and worker are the source of truth, so a disconnected session cannot erase or silently complete a customer run.

## Provider architecture

Each external provider is an adapter behind the workflow. The Factory owns policy, state, retry budget, evidence, and stage transitions. Provider adapters own API calls. This keeps customer workflows portable across model, repository, hosting, and output providers.
