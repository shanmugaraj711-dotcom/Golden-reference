# Phase 3 — Controlled Coding-Agent Integration

## Objective

Connect the Project Factory to a real coding-agent worker without weakening the factory's evidence, scope, retry, or release gates.

## Worker

The first production-grade worker boundary is `CodexCliAgent`.

OpenAI's Codex CLI supports non-interactive `codex exec` for automation and CI/CD. The adapter invokes it with an explicit workspace, JSON event output, an ephemeral session, and the `workspace-write` sandbox. It never uses the dangerous full-access bypass mode.

## Factory connection

`AgentTask` is the bridge:

```text
ProjectFactory
   ↓ Task
AgentTask
   ↓ instruction + workspace
CodexCliAgent
   ↓
Codex CLI
   ↓
changed files + exit code + event evidence
   ↓
ProjectFactory evidence
   ↓
TEST → VERIFY → REGRESSION → RELEASE
```

The agent is a worker, not the orchestrator. A successful agent exit alone does not make the project complete; the factory still requires its downstream gates.

## Controlled fixture smoke

`scripts/codex_fixture_smoke.py` creates an isolated temporary Git repository from `fixtures/sample_project`, runs one Codex task, and reports machine-readable success, changed files, exit code, and evidence. The original repository is not given write access by this smoke test.

`.github/workflows/codex-fixture-smoke.yml` exposes the smoke test through manual `workflow_dispatch`. It requires the repository secret `OPENAI_API_KEY`, installs the official Codex CLI package, and runs only against the temporary fixture.

## Safety controls

- Git repository boundary required.
- Explicit workspace path.
- `workspace-write` sandbox only.
- Ephemeral agent session.
- Timeout enforced by the adapter.
- No arbitrary shell construction from prompt text.
- Changed-file evidence captured before/after the agent run.
- Agent cannot grant itself release or production authority.
- Production deployment remains outside this smoke workflow.

## Gate definition

The integration milestone is PASS when:

1. Unit tests cover the adapter command construction.
2. Factory tests prove AgentTask evidence reaches the run state.
3. The fixture smoke workflow can run with an approved OpenAI credential.
4. A successful agent run produces changed-file and event evidence.
5. A failed/timeout agent run returns a non-success result and remains subject to the factory's bounded repair policy.

## Next milestone

After the fixture smoke passes, run the factory against a small second project with a real coding task. That project must be independent of PromptStudio.ai. The second-project run is the first meaningful proof that the workflow generalizes beyond the golden reference.
