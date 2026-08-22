# Project Factory Delivery Runbook

## Delivery modes

### Customer-owned
- Customer repository is the system of record.
- Customer owns the Vercel project/account when possible.
- Factory generates and verifies the project before handoff.
- Transfer credentials or ownership only through the provider's supported controls.

### Managed
- Factory/operator repository and Vercel project remain the system of record.
- Customer receives the live URL and agreed support/maintenance service.
- Ownership and billing terms must be explicit before delivery.

## Factory sequence

1. Capture customer request.
2. Generate project files with the configured AI provider.
3. Reject unsafe paths and malformed file objects.
4. Run the generated-project build gate.
5. Create a SHA-256 delivery manifest.
6. Package the verified artifact.
7. Create a delivery plan for customer-owned or managed mode.
8. Publish to the selected repository only after explicit delivery authorization.
9. Deploy to the selected Vercel target.
10. Verify the deployment URL and retain evidence.

## Zero-cost rule

The Factory defaults to the configured free-tier model and has a spend ceiling of zero. Paid providers or paid infrastructure must never be enabled implicitly.
