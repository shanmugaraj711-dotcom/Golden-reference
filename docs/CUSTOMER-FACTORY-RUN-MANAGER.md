# Customer Factory Run Manager

The Factory is session-independent. A customer project is represented by a persistent `FactoryRun` and its checkpointed state, not by an open ChatGPT session.

## Lifecycle

`INTAKE → PLAN → BUILD → TEST → REPAIR → REPOSITORY → DEPLOY → HEALTH → EVIDENCE → HANDOFF → MANAGED → COMPLETE`

A missing authorization, failed external health check, or exhausted retry budget moves the run to `BLOCKED`. A later worker can call `resume()` and continue from the last completed checkpoint.

## Rules

- Every run has a durable `runId`, `customerId`, and `projectId`.
- Stage completion is explicit; work is not inferred from chat history.
- Retry budgets prevent infinite repair loops.
- Completion is fail-closed: repository, deployment, health, evidence, and handoff must all be proven first.
- Credentials are never stored in run state; providers should use scoped installation/service credentials.
- Workers can be scheduled, restarted, or replaced without losing the run's state.

## Next integration

Persist `FactoryRun.to_dict()` in the existing Firestore project/run record and have a worker claim the next `RUNNING`/resumable `BLOCKED` run. Provider adapters should perform GitHub/Vercel operations and checkpoint only after observable evidence exists.

This separates **orchestration state** from the AI/chat session and makes the same delivery pipeline reusable for every customer.
