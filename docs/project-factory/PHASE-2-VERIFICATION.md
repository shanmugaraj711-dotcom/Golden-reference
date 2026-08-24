# Phase 2 Verification

## Fixture gate matrix

The controlled fixture proves the following behaviors in the deterministic factory:

| Gate | Scenario | Expected |
|---|---|---|
| Happy path | all tasks pass | COMPLETE |
| Transient failure | first attempt fails, second passes | DIAGNOSE → REPAIR → COMPLETE |
| Exception | worker raises | failure becomes evidence; bounded execution |
| Repair budget | permanent failure | BLOCKED after configured budget |
| Resume | completed task exists in checkpoint | completed work is skipped |
| Input validation | duplicate task ID | rejected |

## Adapter matrix

| Adapter | Purpose | Status |
|---|---|---|
| `LocalCommandAdapter` | Execute explicit build/test/verify commands in a checked-out workspace | Implemented |
| `CommandCodingAgent` | Contract boundary for an approved coding-agent CLI | Interface implemented; execution intentionally gated |

## Why the real agent is gated

The factory must not silently execute an arbitrary CLI or turn user prompt text into a shell command. A production coding-agent adapter requires an explicitly approved executable, workspace policy, environment/credential policy, output/evidence capture, timeout limits, and a kill/escalation path.

The current design therefore proves the integration boundary without claiming that a live coding agent has already been connected.

## Exit criteria for this milestone

- Fixture behavior is covered by deterministic tests.
- Failures produce evidence and bounded retries.
- Checkpoints can resume completed work.
- A project adapter can run explicit commands.
- A coding-agent interface exists without unsafe implicit execution.
- CI remains the authoritative automated test gate.

## Batch 2 — Controlled Codex fixture integration

Objective: prove the next controlled integration from the Phase 2 blueprint without touching production or the Golden-reference checkout.

Scope:
- Run the approved Codex CLI only against the temporary fixture.
- Use the bounded adapter and its existing workspace/evidence controls.
- Capture changed-file and command/test evidence.
- Feed the result through the existing factory evidence boundary.
- No production deployment authority and no customer repository writes.

Pass condition: the fixture run completes successfully and produces evidence that the coding-agent adapter executed within the declared boundary.

This batch is intentionally isolated from the production autonomous runner and does not regenerate or redeploy a customer project.

## Next controlled integration

Connect one approved coding-agent CLI through `CodingAgent`, run it only inside an isolated workspace, capture changed files and command/test evidence, and feed the result back through the same Project Factory gates. Do not grant production deployment authority in this phase.
