# Golden-reference

## Project Factory

Golden-reference is the dedicated repository for **Automation #1 — Project Factory**.

Its purpose is to turn a proven software-development workflow into a repeatable, evidence-driven automation pipeline that can build future projects.

### Golden reference

`PromptStudio.ai` is Project #1 and the golden reference implementation. It is **not** the automation repository.

### Current status

- Phase 1 — workflow specification: complete
- Phase 2 — controlled deterministic orchestrator: implemented
- CI contract tests: enabled
- Production autonomy: intentionally not enabled yet

### Pipeline

`Request → Specify → Plan → Build → Test → Verify → Diagnose → Repair → Regression → Release → Checkpoint`

### Design rule

> A model saying "done" is not evidence. A passing, observable check is evidence.

The engine is intentionally small at this stage. We will prove state persistence, bounded repair, checkpoint resume, and truthful completion before adding real coding-agent execution.

See `docs/project-factory/PROJECT-FACTORY-BLUEPRINT.md` and `docs/project-factory/PHASE-2-IMPLEMENTATION.md` for the governing contracts.
