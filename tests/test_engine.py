from project_factory import ProjectFactory, RunResult
from project_factory.engine import Status, Task


def test_successful_run_produces_evidence_and_checkpoint():
    factory = ProjectFactory("run-1", "fixture")
    factory.add_task(Task("hello", "fixture task", lambda: True))

    result = factory.run()

    assert isinstance(result, RunResult)
    assert result.status is Status.COMPLETE
    assert result.state.completed_tasks == ["hello"]
    assert result.state.checkpoint["status"] == "complete"
    assert any(item.stage == "verify" and item.result == "passed" for item in result.state.evidence)


def test_failure_is_bounded_and_blocks():
    factory = ProjectFactory("run-2", "fixture", max_repairs=2)
    factory.add_task(Task("broken", "intentional failure", lambda: False))

    result = factory.run()

    assert result.status is Status.BLOCKED
    assert result.state.failed_tasks == ["broken"]
    assert result.state.blocked_reason
    assert sum(item.result == "failed" for item in result.state.evidence) == 3


def test_checkpoint_can_resume_completed_work():
    first = ProjectFactory("run-3", "fixture")
    first.add_task(Task("one", "first", lambda: True))
    first_result = first.run()
    checkpoint = first_result.state.checkpoint

    resumed = ProjectFactory("run-3", "fixture")
    resumed.add_task(Task("one", "first", lambda: False))
    resumed.resume_from_checkpoint(checkpoint)
    result = resumed.run()

    assert result.status is Status.COMPLETE
    assert result.state.completed_tasks == ["one"]
