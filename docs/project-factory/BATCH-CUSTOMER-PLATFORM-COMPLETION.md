# Batch — Customer Platform Completion

## Goal
Move Golden Reference from a verified delivery engine to a customer-ready platform without adding recurring CI jobs or changing the approved delivery UI.

## Included in this batch

1. Customer authentication and ownership — Firebase ID-token verification is supported by the API; project reads/writes are scoped to the authenticated UID.
2. Real project creation/intake — authenticated customers can create a project with name, brief, and delivery model.
3. Rate limiting — API routes have a bounded per-IP soft limiter; production should additionally use Cloudflare/Firebase App Check for durable abuse protection.
4. Fresh-destination acceptance — the project model preserves deployment, health, ownership, and evidence gates so a fresh project cannot be marked delivered without them.
5. Managed change/redeploy — managed projects are enrolled automatically and customer change requests are persisted with version/status context for factory review.
6. Customer change-request E2E surface — customer portal can submit a request; factory/admin can consume it through the existing project control path.
7. Production monitoring — a health endpoint can probe the configured production URL and report HTTP status and latency.
8. Support/SLA path — support requests are persisted as project-scoped requests with priority and timestamp; SLA policy remains an operational configuration rather than hidden magic.
9. Local-model runtime — configurable OpenAI-compatible local model proxy is available through `LOCAL_MODEL_URL` and can be used by the factory adapter.
10. Billing/payment — Stripe Checkout adapter is implemented behind `STRIPE_SECRET_KEY` + `STRIPE_PRICE_ID`; it remains disabled until real commercial credentials and pricing are configured.

## Required production activation

The code deliberately does not invent external credentials or pretend external services are active. Before claiming the platform is commercially live, configure:

- `FIREBASE_WEB_API_KEY`
- `FIREBASE_AUTH_DOMAIN`
- `FIREBASE_PROJECT_ID`
- `FIREBASE_APP_ID`
- `FIREBASE_AUTH_REQUIRED=true`
- `PRODUCTION_HEALTH_URL`
- `LOCAL_MODEL_URL` and optional `LOCAL_MODEL_NAME`
- `STRIPE_SECRET_KEY` and `STRIPE_PRICE_ID`
- `RATE_LIMIT_PER_MINUTE` as the product baseline

For public production traffic, enable Firebase App Check / reCAPTCHA Enterprise and enforce it after monitoring legitimate traffic. Firebase documents App Check as complementary to Authentication and recommends it for public backends. 

## Acceptance gate

A release is not called complete until one fresh customer account can:

`Sign up → Sign in → Create project → See only owned project → Factory build → Verify → Deploy → Live health → Delivered → Request managed change → Factory review → Redeploy → New version → Health check → Delivered again`

Billing is separately accepted with a real Stripe test-mode checkout and webhook/fulfilment verification. Local-model acceptance requires one real inference through the configured local endpoint and one second-project factory execution.

## Deployment discipline

This batch is designed to land as one release merge. No recurring GitHub workflow is added.
