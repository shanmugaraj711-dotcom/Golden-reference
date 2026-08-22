# V3 E2E Evidence Record

A real acceptance run must produce one immutable record containing:

- `runId`: unique acceptance run identifier
- `mode`: `transfer` | `deploy` | `managed`
- `requestId`: originating customer request
- `destination`: authorized repository/hosting target
- `artifact`: generated artifact identifier and manifest reference
- `qualityGate`: PASS/FAIL
- `delivery`: HANDOFF/DEPLOYED/FAILED
- `deploymentId`: deployment identifier when applicable
- `productionUrl`: live URL when applicable
- `healthCheck`: PASS/FAIL/NOT_REQUIRED
- `version`: delivered version
- `previousVersion`: required for change/redeploy runs
- `dashboardState`: final customer-facing state
- `timestamp`: UTC completion time

## Pass criteria
Transfer requires quality PASS, successful handoff and destination verification.
Deploy requires quality PASS, successful deployment, production URL and external health-check PASS.
Managed requires all Deploy criteria plus a change request, a new version, preserved previous-version evidence and successful redeployment.
