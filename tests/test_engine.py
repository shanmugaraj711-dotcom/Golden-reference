from project_factory import ProjectFactory, RunResult
from project_factory.agent_adapter import AgentResult, AgentTask
from project_factory.engine import Status, Task


def test_happy_path_runs_all_gates():
    factory = ProjectFactory("run-1", "fixture-happy", max_repairs=3)
    for name in ("requirements", "build", "api", "ui"):
        factory.add_task(Task(name, name, lambda: True))

    result = factory.run()

    assert isinstance(result, RunResult)
    assert result.status is Status.COMPLETE
    assert result.state.failed_tasks == []
    assert result.state.completed_tasks == ["requirements", "build", "api", "ui"]
    assert result.state.checkpoint["status"] == "complete"
    assert any(e.stage == "verify" and e.result == "passed" for e in result.state.evidence)
    assert any(e.stage == "regression" and e.result == "passed" for e in result.state.evidence)


def test_transient_failure_is_repaired_and_verified():
    attempts = {"count": 0}

    def flaky():
        attempts["count"] += 1
        return attempts["count"] >= 2

    factory = ProjectFactory("run-2", "fixture-repair", max_repairs=3)
    factory.add_task(Task("api", "API", flaky))

    result = factory.run()

    assert result.status is Status.COMPLETE
    assert attempts["count"] == 2
    assert any(e.stage == "diagnose" for e in result.state.evidence)
    assert any(e.stage == "repair" for e in result.state.evidence)


def test_exception_becomes_failure_evidence():
    def broken():
        raise RuntimeError("fixture failure")

    factory = ProjectFactory("run-3", "fixture-exception", max_repairs=0)
    factory.add_task(Task("broken", "Broken task", broken))

    result = factory.run()

    assert result.status is Status.BLOCKED
    assert "broken" in result.state.failed_tasks
    assert any("fixture failure" in e.detail for e in result.state.evidence)


def test_repair_budget_blocks_permanent_failure():
    factory = ProjectFactory("run-4", "fixture-budget", max_repairs=2)
    factory.add_task(Task("always-fails", "Permanent failure", lambda: False))

    result = factory.run()

    assert result.status is Status.BLOCKED
    assert result.state.blocked_reason == "Task always-fails exceeded repair budget"
    assert result.state.checkpoint["status"] == "blocked"
    assert sum(item.result == "failed" for item in result.state.evidence) == 3


def test_checkpoint_resume_skips_completed_work():
    calls = {"first": 0, "second": 0}

    factory = ProjectFactory("run-5", "fixture-resume", max_repairs=1)
    factory.add_task(Task("first", "First", lambda: calls.__setitem__("first", calls["first"] + 1) or True))
    factory.add_task(Task("second", "Second", lambda: calls.__setitem__("second", calls["second"] + 1) or True))
    first_result = factory.run()
    checkpoint = first_result.state.checkpoint

    resumed = ProjectFactory("run-5", "fixture-resume", max_repairs=1)
    resumed.add_task(Task("first", "First", lambda: calls.__setitem__("first", calls["first"] + 1) or True))
    resumed.add_task(Task("second", "Second", lambda: calls.__setitem__("second", calls["second"] + 1) or True))
    resumed.resume_from_checkpoint(checkpoint)
    second_result = resumed.run()

    assert second_result.status is Status.COMPLETE
    assert calls["first"] == 1
    assert calls["second"] == 1


def test_duplicate_task_ids_are_rejected():
    factory = ProjectFactory("run-6", "fixture-validation")
    factory.add_task(Task("same", "one", lambda: True))
    try:
        factory.add_task(Task("same", "two", lambda: True))
        assert False, "duplicate task id should fail"
    except ValueError as exc:
        assert "Duplicate task id" in str(exc)


class FakeAgent:
    def execute(self, instruction: str, *, workspace: str) -> AgentResult:
        return AgentResult(True, f"executed: {instruction}", ["fixture.txt"], ["agent event"])


def test_agent_task_is_executed_and_evidence_reaches_factory():
    agent_task = AgentTask(FakeAgent(), "improve fixture", "/tmp/fixture")
    factory = ProjectFactory("run-7", "fixture-agent", max_repairs=0)
    factory.add_task(Task("agent", "Agent implementation", agent_task))

    result = factory.run()

    assert result.status is Status.COMPLETE
    assert agent_task.last_result is not None
    assert any("executed: improve fixture" in e.detail for e in result.state.evidence)
    assert any("agent event" in e.detail for e in result.state.evidence)
