# Project Factory V2 Runbook

## Customer delivery models

### 1. Transfer
Build and validate the project, publish the handoff artifact, and transfer repository/ownership to the customer. No ongoing Factory maintenance is promised.

### 2. Deploy
Build and validate the project, publish it to the customer's destination, verify the live URL, and provide the production handoff. This is the default live-site model.

### 3. Managed
Build, validate, deploy, and retain the operational relationship for ongoing maintenance, updates, health checks, and controlled releases.

## Standard pipeline

Customer request -> generation -> quality gate -> immutable manifest -> destination delivery -> deployment -> health check -> handoff/maintenance status.

## Required evidence

Every generated project must include a `factory-manifest.json` containing the request, model, delivery mode, destination information, gate result, and SHA-256 file inventory.

## Security

- Gemini credentials stay in GitHub Actions secrets.
- Destination credentials are supplied only through `FACTORY_DELIVERY_TOKEN`.
- Generated customer code must not contain provider secrets.
- The Factory must not overwrite a customer's repository unless the destination credential and repository were explicitly supplied.

## Failure policy

- Generation or quality-gate failures stop delivery.
- Destination authentication failures are explicit and do not masquerade as successful delivery.
- Pull-request creation is optional; a published delivery branch remains a valid handoff artifact when repository policy blocks automated PR creation.
- A live URL is considered verified only after an HTTP 200 health check.

## Acceptance checklist

- [ ] Transfer model passes automated tests.
- [ ] Deploy model passes automated tests.
- [ ] Managed model passes automated tests.
- [ ] Gemini generation succeeds with the configured free-tier model.
- [ ] Generated project passes the quality gate.
- [ ] Manifest is produced and archived.
- [ ] Destination repository delivery succeeds when authorized.
- [ ] Production deployment succeeds for a destination connected to Vercel.
- [ ] Live URL returns HTTP 200 when supplied.
- [ ] Handoff and maintenance expectations are recorded in the manifest.
