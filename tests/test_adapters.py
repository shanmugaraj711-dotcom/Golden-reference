from pathlib import Path
import subprocess

from project_factory.adapters import LocalCommandAdapter
from project_factory.agent_adapter import AgentResult, CodexCliAgent, CommandCodingAgent


def test_local_adapter_runs_allowlisted_commands(tmp_path: Path):
    adapter = LocalCommandAdapter(
        tmp_path,
        commands={
            "prepare": ["python", "-c", "print('prepared')"],
            "build": ["python", "-c", "print('built')"],
            "test": ["python", "-c", "print('tested')"],
            "verify": ["python", "-c", "print('verified')"],
        },
    )

    assert adapter.prepare().passed
    assert adapter.build().passed
    assert adapter.test().passed
    assert adapter.verify().passed


def test_missing_adapter_command_is_a_failure(tmp_path: Path):
    result = LocalCommandAdapter(tmp_path).test()
    assert not result.passed
    assert result.returncode != 0


def test_coding_agent_contract_is_explicitly_not_enabled():
    agent = CommandCodingAgent(["approved-agent"])
    try:
        agent.execute("build fixture", workspace=".")
        assert False, "agent execution must remain disabled until configured"
    except RuntimeError as exc:
        assert "intentionally disabled" in str(exc)


def test_codex_adapter_requires_a_git_workspace(tmp_path: Path):
    agent = CodexCliAgent()
    try:
        agent.execute("inspect", workspace=str(tmp_path))
        assert False, "non-git workspace should be rejected"
    except RuntimeError as exc:
        assert "git" in str(exc).lower()


def test_codex_adapter_builds_sandboxed_command(monkeypatch, tmp_path: Path):
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        if command[:2] == ["git", "rev-parse"]:
            return subprocess.CompletedProcess(command, 0, str(tmp_path) + "\n", "")
        if command[:2] == ["git", "status"]:
            return subprocess.CompletedProcess(command, 0, " M app.py\n", "")
        return subprocess.CompletedProcess(command, 0, '{"type":"turn.completed"}\n', "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = CodexCliAgent(model="gpt-5.3-codex").execute("fix the fixture", workspace=str(tmp_path))

    command = next(call[0] for call in calls if call[0][0] == "codex")
    assert command[:3] == ["codex", "exec", "--ephemeral"]
    assert "--sandbox" in command and "workspace-write" in command
    assert "--json" in command
    assert "--model" in command and "gpt-5.3-codex" in command
    assert result.success is True
    assert result.returncode == 0


def test_agent_result_is_machine_readable():
    result = AgentResult(True, "changed fixture", ["app.py"], ["tests passed"])
    assert result.success is True
    assert result.changed_files == ["app.py"]
