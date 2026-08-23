# Admin Factory Control

The Admin surface is the human control plane for the autonomous customer factory.

## Execution modes

- **Full automation:** start `1 → 10`.
- **Bounded execution:** start any valid range, e.g. `1 → 5`.
- **Targeted revision:** create a new version from any stage, e.g. `4 → 10`.
- **Pause / resume:** preserve the current version and checkpoint.
- **Approve:** mark the current version approved for the next delivery policy.

## Version policy

Customer feedback never mutates a delivered version. A revision creates `V(n+1)` and records the requested instruction plus the selected start/end stage.

## Output targets

The workflow stores an output target such as `web`, `android`, or `ios`. Provider-specific packaging/deployment adapters consume that target; the workflow controller does not hard-code a single destination.

## Worker boundary

The UI issues commands. A persistent worker executes stages and checkpoints observable evidence. Chat sessions are not the source of truth. The worker may continue after the admin leaves the browser and can resume a blocked run from its persisted state.
