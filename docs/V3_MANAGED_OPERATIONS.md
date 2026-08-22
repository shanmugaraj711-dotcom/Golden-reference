# V3 Managed Operations

## Managed project record
- Customer/project identifier
- Current production version
- Hosting target
- Repository
- Health status
- Last successful deployment
- Last verified health check
- Open change requests
- Maintenance status

## Operational lifecycle
REQUEST → TRIAGE → PLAN → CHANGE → QUALITY_GATE → DEPLOY → HEALTH_CHECK → RECORD

## Safety
- Keep the previous known-good version available for rollback where the hosting platform supports it.
- Never deploy a failed quality gate.
- Never mark a project healthy without a live check.
- Never expose provider credentials.
- Record every production change with version and timestamp evidence.
