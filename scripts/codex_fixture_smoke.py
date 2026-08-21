from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

from project_factory.agent_adapter import CodexCliAgent


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("instruction")
    args = parser.parse_args()

    source = Path("fixtures/sample_project").resolve()
    with tempfile.TemporaryDirectory(prefix="project-factory-codex-") as tmp:
        workspace = Path(tmp) / "fixture"
        shutil.copytree(source, workspace)
        subprocess.run(["git", "init", "-q"], cwd=workspace, check=True)
        subprocess.run(["git", "add", "."], cwd=workspace, check=True)
        subprocess.run(
            ["git", "-c", "user.name=Project Factory", "-c", "user.email=factory@example.invalid", "commit", "-qm", "fixture"],
            cwd=workspace,
            check=True,
        )

        result = CodexCliAgent(timeout_seconds=900).execute(args.instruction, workspace=str(workspace))
        print(json.dumps({
            "success": result.success,
            "summary": result.summary,
            "changedFiles": result.changed_files,
            "evidence": result.evidence,
            "returncode": result.returncode,
        }, indent=2))
        return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
