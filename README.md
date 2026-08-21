# Golden-reference

## Project Factory

Golden-reference is the dedicated repository for **Automation #1 — Project Factory**.

Its purpose is to turn a proven software-development workflow into a repeatable, evidence-driven automation pipeline that can build future projects.

### Golden reference

`PromptStudio.ai` is Project #1 and the golden reference implementation. It is **not** the automation repository.

### Current status

- Phase 1 — workflow specification: complete
- Phase 2 — controlled deterministic orchestrator: complete
- Fixture gates: implemented and covered by tests
- Project adapter boundary: implemented
- Coding-agent task bridge: implemented
- Real Codex CLI adapter: implemented with sandbox, timeout, Git workspace, and evidence controls
- Controlled Codex fixture smoke workflow: ready (`workflow_dispatch`)
- Production autonomy: intentionally not enabled yet

### Pipeline

`Request → Specify → Plan → Build → Test → Verify → Diagnose → Repair → Regression → Release → Checkpoint`

### Design rule

> A model saying "done" is not evidence. A passing, observable check is evidence.

### Safety rule

The factory does not convert arbitrary prompt text into shell commands or grant production deployment authority to an agent. Coding-agent execution is isolated to an explicit workspace, uses a bounded sandbox and timeout, captures changed-file evidence, and remains subject to the factory's downstream gates.

### Verification

The deterministic fixture suite covers happy path, transient repair, exceptions, repair budgets, checkpoint resume, validation, adapter behavior, and factory-to-agent evidence propagation.

The manual Codex fixture smoke workflow runs the real Codex CLI against a temporary Git fixture only. It requires an approved `OPENAI_API_KEY` repository secret and never writes to the Golden-reference checkout.

See:
- `docs/project-factory/PROJECT-FACTORY-BLUEPRINT.md`
- `docs/project-factory/PHASE-2-IMPLEMENTATION.md`
- `docs/project-factory/PHASE-2-VERIFICATION.md`
- `docs/project-factory/PHASE-3-CODEX-INTEGRATION.md`
