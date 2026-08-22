# V3 E2E Acceptance Runbook

## Purpose
Prove the three customer delivery models against fresh destinations. Contract tests are not production evidence.

## Transfer
1. Submit a fresh project request.
2. Generate and validate artifacts.
3. Authorize a fresh destination repository.
4. Deliver without publishing to PromptStudio production.
5. Verify destination files and manifest.
6. Record handoff evidence.

Expected terminal state: HANDED_OFF.

## Deploy
1. Submit a fresh project request.
2. Generate and validate artifacts.
3. Authorize a fresh destination repository and hosting target.
4. Deliver and deploy.
5. Perform an external HTTP health check.
6. Confirm dashboard reads the persisted delivery evidence.

Expected terminal state: LIVE.

## Managed
1. Complete the Deploy flow.
2. Submit a customer change request.
3. Generate a new version and run quality gates.
4. Preserve version 1 evidence.
5. Deploy version 2 to the authorized destination.
6. Perform an external health check.
7. Confirm dashboard shows version 2 and managed state.

Expected terminal state: MANAGED.

## Evidence requirements
Each run must retain: request ID, destination authorization, generated artifact/manifest, quality result, deployment ID/URL where applicable, health-check result, final dashboard state, and version history.

Do not mark a run passed from a unit test alone. A fresh destination and observable deployment/health evidence are required for Deploy and Managed.
