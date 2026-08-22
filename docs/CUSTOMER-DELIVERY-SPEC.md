# Customer Delivery Specification

## Principle

**Build with our factory. Deliver according to the customer's ownership needs.**

GitHub and Vercel are implementation infrastructure. They are not automatically the customer's required accounts.

## Request contract

Every project request records:

- customer/project ID
- requested product type
- acceptance criteria
- package/scope
- delivery mode: `managed`, `handover`, or `hybrid`
- required outputs
- domain requirements
- hosting requirements
- mobile store requirements when applicable
- data/database requirements
- third-party integrations
- support/maintenance choice

## Delivery matrix

| Output | Default build location | Customer receives | Ownership decision |
|---|---|---|---|
| Website/web app | Factory workspace + staging | live URL + source/package | managed, handover, or hybrid |
| API/backend | Factory workspace + staging | endpoint + source/docs | managed, handover, or hybrid |
| Android | Factory workspace | source + APK/AAB when buildable | customer store/account when publishing |
| iOS | Factory workspace | source + archive/build when environment permits | customer Apple account for production publishing |
| SaaS/internal tool | Factory workspace + staging | live product + source/docs | managed or handover |
| Automation/integration | Factory workspace | workflow/source + documentation | customer or managed |

## Ownership rules

### Managed

We retain operational control of the agreed hosting environment. The customer receives the finished product and support terms. This creates a potential recurring service relationship.

### Handover

Critical production resources should be created in or transferred to customer-controlled accounts when supported by the platform. Never request a customer's long-lived credentials to store in the repository.

### Hybrid

We operate the product while customer-controlled ownership is established for critical assets such as domain, app-store identity, payment accounts, and other non-transferable production identities where practical.

## Quality gate

A delivery package is complete only when:

1. acceptance criteria pass;
2. build/test evidence exists;
3. verification evidence exists;
4. required artifacts are present;
5. ownership mode is recorded;
6. deployment status is known;
7. handover documentation exists when applicable;
8. final checkpoint is stored.

## Important limitation

Not every platform supports transfer of every resource. The factory must inspect the actual project requirements before promising a transfer. For mobile apps, production signing and store publishing normally require the customer's own developer identity/account.

## Customer-facing promise

The customer does **not** need to learn GitHub, Vercel, AI models, coding agents, or local development unless they explicitly choose a technical handover.
