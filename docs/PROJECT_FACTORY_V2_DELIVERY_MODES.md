# Project Factory V2 — Delivery Modes

Project Factory supports three customer delivery models.

## 1. Transfer
Customer owns the destination repository and hosting account.

Flow:
1. Capture request and destination.
2. Generate with Gemini.
3. Run the project gate.
4. Create manifest and evidence.
5. Publish to the authorized customer repository.
6. Customer hosting deploys from that repository.
7. Run live health check when a URL is supplied.
8. Hand over source, URL, manifest, and operating notes.

Factory responsibility ends at the agreed handoff unless maintenance is purchased.

## 2. Managed
Factory/agency keeps the operational responsibility.

Flow is the same through deployment, followed by:
- monitoring and incident response;
- fixes and redeployments;
- dependency/security maintenance;
- backups/export where applicable;
- periodic ownership and access review.

The customer receives a live URL and a defined support path.

## 3. Demo / Decide Later
Used for trials, prototypes, or customers who have not selected ownership yet.

The Factory creates an isolated destination and clearly marks it as provisional. Before commercial handoff, the customer chooses Transfer or Managed.

## Safety rules
- Never deploy customer work into PromptStudio production by default.
- Never place customer secrets in generated source.
- Never report deployment success without a live verification when a URL is available.
- Destination credentials are supplied only through GitHub/Vercel secret mechanisms.
- Every generated delivery includes a manifest with file hashes.
- A failed optional PR step must not invalidate a successfully published delivery branch.

## Commercial lifecycle
Request → scope → generate → validate → destination → deploy → verify → handoff → maintain/renew.
