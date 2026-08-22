# Destination Delivery V2

The Factory supports three customer delivery modes.

## 1. Transfer
Customer owns the destination repository and hosting account. The Factory prepares and verifies the artifact, then publishes only to an explicitly authorized customer destination. Final ownership/access is handed to the customer.

## 2. Managed
The Factory/operator owns the deployment environment and maintains the application. Customer receives the live service and agreed support. Billing and maintenance terms are explicit.

## 3. Decide Later
The Factory temporarily uses a controlled delivery environment. Before final handoff, the customer chooses Transfer or Managed.

## Destination requirements

A delivery execution must have an explicit destination repository and hosting target. The Factory must never silently deploy customer output into PromptStudio production.

## Execution contract

1. Generate and validate artifact.
2. Produce manifest/evidence.
3. Resolve delivery mode.
4. Resolve authorized destination repository.
5. Resolve authorized hosting project.
6. Publish/transfer according to mode.
7. Deploy.
8. Health-check the live URL.
9. Record delivery evidence.
10. Handoff or activate maintenance.

If a destination authorization is unavailable, the workflow stops at the authorization boundary rather than claiming deployment success.
