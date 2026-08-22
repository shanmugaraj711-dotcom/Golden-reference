# Project Factory Operations Contract

## Customer lifecycle

1. Intake — capture business goal, required pages/features, brand assets, integrations, destination owner, and delivery model.
2. Generate — use the configured Gemini provider with the current approved model.
3. Gate — validate structure, required files, unsafe/missing configuration, and delivery manifest.
4. Deliver — publish only to the explicitly authorized destination.
5. Deploy — use the customer's or managed hosting destination.
6. Verify — perform a live HTTP health check when a destination URL is available.
7. Handoff — provide repository, deployment URL, manifest, run record, and support instructions.
8. Maintain — for managed customers, track fixes, redeployments, dependency updates, and support events.

## Delivery modes

- **Transfer:** customer owns repository and hosting; Factory hands over the completed project.
- **Managed:** Factory operates repository/hosting under an agreed maintenance scope.
- **Demo:** isolated provisional environment until customer selects Transfer or Managed.

## Required acceptance evidence

- generation completed;
- project gate passed;
- delivery manifest created;
- destination identified explicitly;
- deployment reached Ready/production when applicable;
- live URL verified when supplied;
- ownership and maintenance mode recorded.

## Security rules

- Secrets live only in GitHub/Vercel environment variables or equivalent secret stores.
- Generated source never contains API keys or access tokens.
- Production PromptStudio infrastructure is never used as a customer destination by default.
- Customer destinations require explicit authorization and least-privilege credentials.
