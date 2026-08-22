# V3 Acceptance Matrix

| Scenario | Required evidence |
|---|---|
| Build & Transfer | validated artifact, manifest, authorized repo, handoff package |
| Build & Deploy | validated artifact, manifest, authorized repo, hosting deployment, live health check |
| Managed | validated artifact, manifest, managed hosting deployment, live health check, maintenance record |
| Authorization blocked | workflow stops safely with explicit BLOCKED_AUTHORIZATION |
| Quality failure | delivery blocked; no production publish |
| Health check failure | deployment not marked LIVE |
| Customer change request | returns to generation/review without losing delivery evidence |

A scenario is complete only when every required evidence item exists. Tests must assert both successful paths and safety-stop paths.
