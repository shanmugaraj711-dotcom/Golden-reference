# Second-project proof gate

The factory is not considered reusable merely because its fixture passes. The next proof is a deliberately small second project that is unrelated to PromptStudio.ai.

## Required evidence

1. Factory receives a natural-language project instruction.
2. A real coding-agent worker executes inside an isolated Git workspace.
3. The worker creates/changes the project files.
4. Factory captures worker evidence.
5. Build/test/verification gates pass.
6. A failure, if introduced, is diagnosed and repaired within the configured budget.
7. Final checkpoint records the completed project and evidence.

## Safety boundary

The second-project proof must not use production credentials, production databases, or production deployment authority. The workspace is disposable and the agent is restricted to the project workspace.

## Success definition

The proof is successful only when the resulting project can be independently inspected and its acceptance criteria reproduced from the checkpoint/evidence record.
