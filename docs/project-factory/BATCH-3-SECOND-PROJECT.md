# Batch 3 — Second-project generalization

## Goal
Prove the factory generalizes beyond the PromptStudio.ai golden reference without enabling autonomous production deployment.

## Independent project
`fixtures/second_project` is a small standalone browser application: a local-only task board with add, complete/uncomplete, delete, clear-completed, and localStorage persistence.

## Controlled coding task
Implement the task-board behavior in `app.js` while preserving the supplied HTML/CSS contract. The task is intentionally independent of PromptStudio.ai and uses no credentials or external services.

## Acceptance criteria
1. Empty state renders on first load.
2. A non-empty trimmed task can be added.
3. Blank/whitespace-only input is rejected.
4. Tasks can be toggled complete and back to active.
5. Tasks can be deleted individually.
6. Clear-completed removes only completed tasks.
7. Reload persistence uses localStorage.
8. Invalid/missing persisted JSON falls back safely to an empty list.
9. The project remains static and deployable with no build command.

## Evidence contract
Batch 3 is considered implementation-complete when the fixture, task specification, deterministic verifier, and checkpoint are committed together. Runtime/browser execution remains a separate gate; this batch deliberately does not create or enable a GitHub Actions job.

## Scope boundary
No production credentials, deployment authority, new workflow, or autonomous release path is introduced in Batch 3.
