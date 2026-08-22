# V3 Project State Machine

Allowed forward lifecycle:
`INTAKE -> PLANNING -> GENERATING -> REVIEW -> APPROVED -> DELIVERING -> VERIFYING -> LIVE -> HANDED_OFF`

Managed lifecycle:
`LIVE -> MANAGED -> CHANGE_REQUEST -> GENERATING -> REVIEW -> APPROVED -> DELIVERING -> VERIFYING -> MANAGED`

Safety states:
- `BLOCKED_AUTHORIZATION`
- `GENERATION_FAILED`
- `QUALITY_FAILED`
- `DELIVERY_FAILED`
- `HEALTHCHECK_FAILED`

Rules:
- Safety failures cannot silently advance to a success state.
- LIVE requires deployment plus health-check PASS.
- HANDED_OFF requires successful transfer evidence.
- Managed redeploy must create a new version and preserve the previous version record.
- Customer-facing state must be derived from persisted evidence.
