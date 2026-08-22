# V3 Release Criteria

A V3 release is production-ready only when:

1. A customer can create/submit a project request.
2. The Factory generates and validates an artifact.
3. The customer can select Transfer, Deploy or Managed.
4. Destination authorization is explicit.
5. Delivery evidence is persisted.
6. Deploy/Managed projects have a verified live endpoint.
7. The dashboard reflects the persisted project record rather than demo data.
8. A customer change creates a new version without destroying prior evidence.
9. Managed changes can be deployed and verified safely.
10. Authentication and ownership prevent cross-customer access.
11. Rate limits, audit logging and secret rotation controls are operational.
12. Production acceptance runs exist for all three delivery models.
13. Monitoring and support procedures are ready.

A documentation checklist is not sufficient evidence; acceptance must be backed by executable tests or observable production records.
