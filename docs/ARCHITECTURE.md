# Project Factory Architecture

## Customer flow

`Phone/browser → request → package → Project Factory → AI worker → workspace → tests → verify → delivery mode → customer`

## Control plane

GitHub is the source-control and audit plane for factory work. The factory owns project state, tasks, evidence, checkpoints, repair budgets, and release decisions.

## Build plane vs customer ownership

**Our build plane is not the customer's product ownership.** We may use our GitHub/Vercel accounts as internal build infrastructure during development and demo work. A production customer project must have an explicit delivery mode before release.

### Delivery modes

1. **Managed** — we host and maintain the product. Our infrastructure remains the operational home; the customer receives the live product and agreed support. Any recurring hosting/maintenance fee is separate from the build price.
2. **Handover** — the customer owns the production resources. We transfer/provision the source repository, hosting project, domains, app-store resources, and required credentials into customer-controlled accounts wherever the platform supports ownership transfer.
3. **Hybrid** — we build and operate the product initially, while customer ownership is established for critical production assets when practical. This is the default model for customers who want low technical effort without permanent lock-in.

The factory must never silently promise that every platform can be transferred. Ownership, billing, domains, app signing, store publishing, databases, and third-party services are checked per project.

## Output types

A project request resolves to one or more deliverables:

- Web application / website
- API / backend service
- Android project plus APK/AAB when the build requirements permit
- iOS project/archive when the required Apple signing/build environment is available
- SaaS/internal tool
- Automation/integration
- Source-code package and deployment documentation

The customer buys the finished deliverable, not access to a specific model, GitHub account, or Vercel account.

## Execution plane

Agent work happens in an isolated project workspace. The agent can modify only the workspace it is assigned. Build, test, verification and release remain factory-controlled gates.

## Release gate

No delivery occurs until the factory has:

- acceptance criteria
- build/test evidence
- verification evidence
- security/configuration checks appropriate to the output
- artifact manifest
- ownership/delivery mode recorded
- final checkpoint

## AI plane

The factory talks to a vendor-neutral provider interface. Providers may be local/open-weight, external, or a future in-house model. Provider choice must never bypass factory verification.

## Cost principle

Prefer the lowest-cost capable provider. Use local/open-weight inference when configured infrastructure can handle the workload. External models are optional fallbacks and must respect the zero-cost-first policy. Measure actual cost per successful project rather than assuming zero cost.

## Security principle

No production credentials in agent workspaces. No arbitrary shell construction from natural-language input. No production deployment authority by default. Every release requires observable evidence.

## Product promise

Customers get a finished project with a clear delivery/ownership model. Internal model, GitHub, and hosting choices should not require a customer-facing product change.