# V3 Customer Change Request Flow

1. Customer opens a live or review project.
2. Customer submits a change request against the current version.
3. Factory records the request and acceptance criteria.
4. Existing delivery evidence remains immutable for the previous version.
5. Factory generates the next version.
6. Quality gate runs against the requested change and existing acceptance criteria.
7. Preview is produced when approval is required.
8. Customer approves or requests another revision.
9. Approved version follows the same authorized destination delivery path.
10. New deployment receives a new version/evidence record.

## Rules
- Never overwrite historical delivery evidence.
- Never publish a requested change before approval when approval is required.
- Never broaden destination permissions because of a change request.
- A failed change must leave the previous live version intact when rollback is available.
