from pathlib import Path
import subprocess

import pytest

from project_factory.agent_adapter import CodexCliAgent


def git_repo(tmp_path: Path) -> Path:
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    return tmp_path


def test_rejects_unsafe_sandbox():
    with pytest.raises(ValueError, match="workspace-write"):
        CodexCliAgent(sandbox="danger-full-access")


def test_rejects_unbounded_timeout():
    with pytest.raises(ValueError, match="one-hour"):
        CodexCliAgent(timeout_seconds=3601)


def test_rejects_empty_instruction(tmp_path, monkeypatch):
    workspace = git_repo(tmp_path)
    agent = CodexCliAgent()
    with pytest.raises(ValueError, match="must not be empty"):
        agent.execute("   ", workspace=str(workspace))


def test_requires_repository_root(tmp_path):
    root = git_repo(tmp_path)
    nested = root / "nested"
    nested.mkdir()
    agent = CodexCliAgent()
    with pytest.raises(ValueError, match="repository root"):
        agent.execute("inspect", workspace=str(nested))
