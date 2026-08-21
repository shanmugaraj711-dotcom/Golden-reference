# Project Factory — Phase 2 Implementation

## Objective
Build the smallest controlled orchestrator that can execute the Phase 1 specification against a test project while preserving state and evidence.

## v0.1 Scope

The first engine is deliberately narrow. It supports a deterministic project lifecycle before adding broad autonomous coding capability.

### Inputs
- Natural-language project request
- Project workspace/repository
- Execution policy

### Outputs
- Normalized project specification
- Ordered task graph
- Execution records
- Test/verification evidence
- Checkpoint
- Final status: `COMPLETE`, `BLOCKED`, or `FAILED`

## Execution Contract

```text
REQUEST
  -> SPEC
  -> PLAN
  -> TASKS
  -> EXECUTE
  -> TEST
  -> VERIFY
  -> REPAIR (bounded)
  -> REGRESSION
  -> RELEASE GATE
  -> CHECKPOINT
```

## State Model

Each run has a durable state object:

```json
{
  "runId": "unique-id",
  "projectId": "project-name",
  "phase": "testing",
  "status": "running",
  "activeTask": "task-id",
  "completedTasks": [],
  "failedTasks": [],
  "attempts": {},
  "evidence": [],
  "decisions": [],
  "blockedReason": null,
  "nextAction": "..."
}
```

State transitions are explicit. A worker cannot silently move a run from failure to completion.

## Evidence Contract

Every action writes an event:

```json
{
  "eventId": "unique-id",
  "runId": "run-id",
  "taskId": "task-id",
  "stage": "test",
  "action": "npm test",
  "result": "passed",
  "evidence": "logs/test-001.txt",
  "timestamp": "ISO-8601"
}
```

Evidence must be addressable and associated with the task that produced it.

## Repair Policy

- Maximum 3 repair attempts per failure in v0.1.
- Each attempt must have a new diagnosis or changed hypothesis.
- Re-run the failed check after every repair.
- Run affected regression checks after a repair passes.
- Escalate instead of looping when the limit is reached.

## Release Gates

A run may reach `RELEASE_READY` only when:

1. Required tasks are complete.
2. Acceptance criteria have evidence-backed PASS status.
3. Build/type/lint checks required by the project pass.
4. Runtime verification passes for critical user flows.
5. No blocking security/configuration finding exists.
6. The checkpoint can reproduce the current state.

## Human Escalation

Pause and return `BLOCKED` for:
- Missing credentials or unavailable external resources.
- Ambiguous business requirements that materially affect behavior.
- Destructive or irreversible production operations.
- Security findings requiring a policy decision.
- Repeated repair failure.

## Golden Reference Validation

PromptStudio.ai is used only as the reference workflow. The automation repository must remain independent of PromptStudio production code.

Validation will happen in this order:

1. Run the orchestrator against a tiny controlled fixture.
2. Verify state persistence and evidence.
3. Verify failure/repair behavior with an intentional test failure.
4. Verify resume-from-checkpoint.
5. Run a small real project.
6. Only then expand toward autonomous project creation.

## Non-Goals

Phase 2 does not attempt to:
- support every framework,
- autonomously deploy production systems,
- bypass human approvals,
- claim full autonomous software development.

## Exit Criteria

Phase 2 is complete when the controlled orchestrator can execute a fixture end-to-end, persist state, produce evidence, recover from a deliberate failure, resume from a checkpoint, and produce a truthful final status.

## Phase 3

Add a real project adapter and controlled coding-agent execution after Phase 2 has passed its fixture gates.
