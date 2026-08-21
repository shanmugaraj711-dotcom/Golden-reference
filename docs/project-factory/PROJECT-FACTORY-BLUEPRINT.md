# Project Factory — Phase 1 Blueprint

## Purpose
Turn the proven PromptStudio.ai development workflow into a repeatable, evidence-driven automation pipeline for future software projects. PromptStudio.ai is the golden reference; this repository is the automation system.

## Core contract
**Human gives intent. The factory plans, executes, tests, repairs, verifies, and reports.** A model saying “done” is never proof. Completion requires observable evidence.

## Pipeline
1. Intake
2. Requirements normalization
3. Acceptance criteria
4. Architecture / implementation plan
5. Task graph
6. Build
7. Automated tests
8. Runtime/browser verification
9. Failure diagnosis
10. Targeted repair
11. Regression verification
12. Security/configuration checks
13. Deployment
14. Production smoke test
15. Final evidence report
16. Checkpoint / handoff

## Stage contract
| Stage | Input | Output | Evidence | Pass condition |
|---|---|---|---|---|
| Intake | User request | Project brief | Captured request | Scope explicit |
| Requirements | Brief | Requirements | Requirements artifact | No critical ambiguity |
| Acceptance | Requirements | Testable criteria | Criteria list | Every feature has a pass condition |
| Plan | Criteria + repo | Architecture + tasks | Plan artifact | Dependencies/order explicit |
| Build | Task | Code/config | Diff/commit | Buildable change |
| Test | Change | Test results | Logs/results | Required tests pass |
| Runtime verify | Running app | User-flow result | Browser/API evidence | Critical flows work |
| Diagnose | Failure evidence | Root cause | Diagnosis record | Failure explained/escalated |
| Repair | Diagnosis | Minimal fix | Diff + retest | Failure resolved |
| Security | Release candidate | Findings | Security checks | No blocking finding |
| Deploy | Release candidate | Deployment | Deployment result | Deployment succeeds |
| Smoke test | Live app | Production validation | Live checks | Critical paths work |
| Handoff | All evidence | Final report/checkpoint | Evidence index | Reproducible state |

## State machine
```text
INTAKE -> SPECIFIED -> PLANNED -> BUILDING -> TESTING -> VERIFYING
                                              | PASS -> RELEASE_READY -> DEPLOYING -> LIVE -> HANDOFF
                                              | FAIL -> DIAGNOSING -> REPAIRING -> REGRESSION_TESTING -> TESTING
Any stage -> BLOCKED/HUMAN_REVIEW -> RESUME
```

## Agent roles
- **Orchestrator:** state, ordering, retries, evidence, checkpoints, escalation.
- **Planner:** requirements, acceptance criteria, architecture, dependencies, tasks.
- **Builder:** smallest safe implementation changes.
- **QA:** deterministic tests and acceptance mapping.
- **Runtime verifier:** browser/API/user-flow validation.
- **Debugger:** evidence-driven root-cause analysis and targeted repair.
- **Security reviewer:** auth, secrets, configuration, endpoints, data boundaries.
- **Release worker:** deployment preparation/execution after gates.
- **Final verifier:** independent outcome verification and evidence report.

## Human control
- **Automatic:** reversible edits, tests, lint/build, local verification, documentation, checkpoints.
- **Approval:** broad architecture changes, production configuration, irreversible migrations, policy-controlled production deployment.
- **Escalation:** missing credentials, material ambiguity, destructive operations, unresolved security issues, repeated repair failure.

## Evidence rules
Every task records: task ID, input, action, changed resources, tool/command, result, evidence location, status, and timestamp.

A task cannot be PASS without evidence. A project cannot be COMPLETE unless every required acceptance criterion has evidence-backed PASS status or an explicit human-approved exception.

## Repair loop
1. Preserve failure evidence.
2. Identify the smallest likely root cause.
3. Change only necessary scope.
4. Re-run failed check.
5. Run affected regression checks.
6. Update diagnosis if still failing; never blindly repeat.
7. Escalate after a bounded repair budget.

## PromptStudio golden reference
The reference project demonstrates a real workflow involving React/Vite/Tailwind, Firebase Auth/Firestore, Vercel serverless APIs, Gemini generation, shared pricing/quota policy, browser/API verification, tests, deployment, and post-deployment validation. It also demonstrates cross-surface verification for referrals, rewards, transactions, founder controls, quotas, support/payment flows, and launch behavior.

## Project memory contract
Every project retains: brief, requirements, acceptance criteria, architecture, task graph, decisions, change log, test evidence, runtime evidence, failures/diagnoses, deployment record, final verification, and next checkpoint. The checkpoint must be sufficient for a future run to resume without reconstructing the full history.

## Phase 1 exit criteria
- Workflow documented as stage contracts.
- Inputs, outputs, evidence, and pass conditions defined.
- Failure/repair behavior defined.
- Human escalation boundaries defined.
- Persistent memory/checkpoint requirements defined.
- PromptStudio identified as golden reference.
- Specification version-controlled and reviewable.

## Boundary
Phase 1 does not replace PromptStudio production architecture, introduce autonomous production deployment, support every technology stack, or claim full autonomy before a second-project proof.

## Phase 2
Implement the smallest controlled orchestrator with persistent state, evidence collection, bounded repair, checkpoint resume, and truthful final status.
