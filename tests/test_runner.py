from pathlib import Path

from project_factory.agent_adapter import AgentResult
from project_factory.runner import FactoryRunner


class FakeAgent:
    def execute(self, instruction: str, *, workspace: str) -> AgentResult:
        assert instruction == "build fixture"
        assert Path(workspace).exists()
        return AgentResult(True, "fixture built", ["fixture.txt"], ["build=pass"])


def test_runner_keeps_agent_inside_factory_gates(tmp_path: Path):
    result = FactoryRunner(FakeAgent(), tmp_path).run(
        "fixture-project", "build fixture", run_id="runner-1"
    )
    assert result.status.value == "complete"
    assert result.state.completed_tasks == ["coding-agent"]
    assert any(e.stage == "verify" and e.result == "passed" for e in result.state.evidence)
    assert any("fixture.txt" in e.detail for e in result.state.evidence)
