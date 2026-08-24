# Project Factory — Foundation Guide

## 1. What this repository is

Golden-reference is the automation system. PromptStudio.ai is the golden-reference application used to prove the workflow.

The factory's job is simple: turn human intent into a tested, verified, evidence-backed software delivery.

## 2. The complete journey

`Request → Requirements → Acceptance → Plan → Build → Test → Runtime Verify → Diagnose/Repair → Security → Deploy → Production Smoke → Handoff`

A project is complete only when the required acceptance criteria have observable evidence.

## 3. System boundaries

- **GitHub:** source control, pull requests, workflow execution, repository secrets, and durable project history.
- **Factory/orchestrator:** owns state, ordering, evidence, checkpoints, repair limits, and truthful status.
- **AI provider:** supplies bounded model capabilities when an approved adapter is invoked. Gemini and Codex are integrations, not the source of truth.
- **Cloudflare/Vercel/etc.:** hosting and deployment targets. A deployment being uploaded is not equivalent to the application being healthy.
- **Browser/API checks:** prove the actual user-facing/runtime behavior.

## 4. Evidence rule

"The model says it works" is not evidence.

Evidence means an observable result: test output, build result, browser/API response, deployment result, health check, changed-file record, or equivalent artifact.

## 5. Failure rule

When a check fails:

1. Preserve the failure evidence.
2. Identify the smallest likely root cause.
3. Apply the smallest safe fix.
4. Re-run the failed check.
5. Run affected regression checks.
6. Escalate instead of looping indefinitely.

Never hide or overwrite a real failure merely to make a run appear successful.

## 6. AI keys

API keys are credentials, not workflow state. They belong in approved secret storage and should only be exposed to the workflow that needs them.

- `GEMINI_API_KEY`: Gemini integration credential.
- `OPENAI_API_KEY`: required only by the real Codex/OpenAI smoke integration; it is unrelated to Gemini.
- `FACTORY_DELIVERY_TOKEN`: factory delivery authentication credential.
- `FIREBASE_SERVICE_ACCOUNT_JSON`: Firebase service credential, only where Firebase operations require it.

An AI provider being available does not mean the factory should use it automatically for every task.

## 7. Workflow rule

Keep workflows small and purposeful. A workflow should have one clear responsibility, explicit permissions, bounded runtime, and a deterministic pass/fail condition.

Manual smoke workflows are validation tools. They are not proof of production readiness by themselves.

## 8. Production rule

Deployment has three separate questions:

1. Did the files/build deploy?
2. Does the live URL respond correctly?
3. Do the critical user flows work?

All three must be distinguished in evidence. A 404 health check is a real failure even when the hosting platform reports a successful upload.

## 9. Human control

Automation may handle reversible implementation, tests, verification, documentation, and checkpoints. Human approval remains appropriate for broad architecture changes, production configuration, destructive operations, security exceptions, and irreversible migrations.

## 10. Definition of Done

A project is DONE when:

- requirements are explicit;
- acceptance criteria are testable;
- implementation is committed;
- required tests pass;
- runtime critical flows pass;
- security/configuration checks pass;
- deployment succeeds;
- production smoke checks pass;
- evidence is retained;
- checkpoint/handoff is reproducible.

## 11. Simplicity principle

Do not add a component because it sounds advanced. Prefer the smallest architecture that satisfies the contract reliably, observably, and securely.
