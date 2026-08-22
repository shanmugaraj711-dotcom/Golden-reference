# V3 Customer Project Record

The persistent project record is the source of truth for the customer dashboard.

Required fields:
- customerId
- projectId
- projectName
- brief
- deliveryModel
- lifecycleState
- currentVersion
- repository
- hostingTarget
- productionUrl
- verification
- ownership
- maintenance
- events
- createdAt
- updatedAt

## Invariants
- `projectId` is unique.
- `customerId` owns the project.
- Every production version has immutable evidence.
- Dashboard state is derived from this record, not hard-coded UI values.
- A project may only transition to LIVE after deployment and health-check evidence.
- A managed change creates a new version while retaining prior evidence.
