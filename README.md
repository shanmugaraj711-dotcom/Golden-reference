# Golden-reference

## Project Factory

Golden-reference is the dedicated repository for **Automation #1 — Project Factory**.

Its purpose is to turn a proven software-development workflow into a repeatable, evidence-driven automation pipeline that can build future projects.

### Golden reference

`PromptStudio.ai` is Project #1 and the golden reference implementation. It is **not** the automation repository.

### Current status

- Phase 1 — workflow specification: complete
- Phase 2 — controlled deterministic orchestrator: implemented
- Fixture gates: implemented and covered by tests
- Project adapter boundary: implemented
- Coding-agent boundary: implemented but safely gated
- CI contract tests: enabled
- Production autonomy: intentionally not enabled yet

### Pipeline

`Request → Specify → Plan → Build → Test → Verify → Diagnose → Repair → Regression → Release → Checkpoint`

### Design rule

> A model saying "done" is not evidence. A passing, observable check is evidence.

### Safety rule

The factory does not convert arbitrary prompt text into shell commands or grant production deployment authority to an agent. A live coding-agent adapter must be explicitly configured with an approved executable, isolated workspace, timeout/kill policy, evidence capture, and escalation rules.

See `docs/project-factory/PROJECT-FACTORY-BLUEPRINT.md`, `docs/project-factory/PHASE-2-IMPLEMENTATION.md`, and `docs/project-factory/PHASE-2-VERIFICATION.md` for the governing contracts.
