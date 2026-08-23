# Customer Automation Batch

## Goal
After Golden Reference is proven, every customer project follows one automated pipeline instead of founder-led manual parcel work.

## Pipeline

`INTAKE -> AUTH -> BUILD -> QUALITY -> REPOSITORY -> DEPLOY -> HEALTH -> EVIDENCE -> HANDOFF -> MANAGED (if selected) -> COMPLETE`

### Rules
- Every stage is idempotent and resumable from a checkpoint.
- Every stage has a bounded retry budget.
- Missing capability/authentication blocks the run; it never fabricates success.
- Deploy requires an explicit hosting target.
- Health requires an external HTTP result.
- Evidence is persisted before terminal completion.
- Transfer stops after handoff; Deploy requires LIVE evidence; Managed requires version/change evidence.

## Customer experience

1. Customer submits project + delivery model.
2. Factory creates a request ID and checkpoint.
3. The automation acquires only the customer's authorized repository/hosting access.
4. Factory builds and runs quality gates.
5. Factory creates/updates the destination branch and delivery artifact.
6. Deploy mode deploys to the authorized Vercel target and verifies the public URL.
7. Dashboard shows the same persisted evidence the worker produced.
8. Managed mode retains version history and processes future change requests through the same pipeline.

## Security model

Use a GitHub App for customer repository automation rather than a personal access token. Installation access tokens are short-lived and can be restricted to selected repositories. Vercel credentials must likewise be stored server-side and scoped to the customer's authorized target. Never expose provider secrets in the customer dashboard.

## Required provider setup for production

One-time founder setup remains unavoidable: install/authorize the automation against the customer's GitHub account/repositories and Vercel target. After authorization, individual projects should not require manual code/deployment work.

## Evidence contract

A run can reach `COMPLETE` only when the requested delivery model's required evidence exists. The automation deliberately fails closed if provider authorization, deployment, health, or evidence capability is unavailable.

## External design references

The architecture follows GitHub's recommended GitHub App model: installation tokens are scoped, short-lived, and attributed to the app rather than a personal account. See GitHub's documentation on GitHub App installation tokens and best practices.
