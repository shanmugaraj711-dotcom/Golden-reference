from pathlib import Path

from project_factory.adapters import LocalCommandAdapter
from project_factory.agent_adapter import AgentResult, CommandCodingAgent


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


def test_agent_result_is_machine_readable():
    result = AgentResult(True, "changed fixture", ["app.py"], ["tests passed"])
    assert result.success is True
    assert result.changed_files == ["app.py"]
