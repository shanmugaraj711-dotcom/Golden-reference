# Project Factory Architecture

## Customer flow

`Phone/browser → request → package → Project Factory → AI worker → GitHub → tests → Vercel → delivery`

## Control plane

GitHub is the source-control and audit plane. The factory owns project state, tasks, evidence, checkpoints, repair budgets, and release decisions.

## AI plane

The factory talks to a vendor-neutral provider interface. Providers may be local/open-weight, external, or a future in-house model. Provider choice must never bypass factory verification.

## Execution plane

Agent work happens in an isolated project workspace. The agent can modify only the workspace it is assigned. Build, test, verification and release remain factory-controlled gates.

## Cost principle

Prefer the lowest-cost capable provider. Use local/open-weight inference when the configured infrastructure can handle the workload. Use external models only when policy permits and local quality/capacity is insufficient. Measure actual cost per successful project rather than assuming zero cost.

## Security principle

No production credentials in agent workspaces. No arbitrary shell construction from natural-language input. No production deployment authority by default. Every release requires observable evidence.

## Customer promise

Customers buy a finished project/service package, not access to a specific model. Internal model/provider changes should not require a customer-facing product change.
