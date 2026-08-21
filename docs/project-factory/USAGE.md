# Project Factory Usage

## Deterministic tests

```bash
python -m pip install -U pytest
pytest -q
```

## Controlled Codex task

With Codex CLI installed and authenticated:

```bash
python scripts/run_project_factory.py \
  --workspace /path/to/git/project \
  --project-id my-project \
  "Implement the requested feature, run the relevant tests, and report the changed files."
```

The runner sends the instruction to `CodexCliAgent`, which invokes `codex exec` in a workspace-write sandbox with a timeout and JSON event capture. The factory then records the worker result as evidence and applies its normal verify, regression, release, and checkpoint gates.

For CI, use `.github/workflows/codex-fixture-smoke.yml`. It intentionally runs only against a temporary fixture and requires an explicitly configured `OPENAI_API_KEY` repository secret.

Never provide production credentials to the fixture workflow and never enable unrestricted sandbox access for the factory.
