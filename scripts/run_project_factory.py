from __future__ import annotations

import argparse
import json

from project_factory import AgentTask, CodexCliAgent, ProjectFactory
from project_factory.engine import Task


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one Project Factory task through Codex")
    parser.add_argument("--workspace", required=True)
    parser.add_argument("instruction")
    parser.add_argument("--run-id", default="local-run")
    parser.add_argument("--project-id", default="project")
    parser.add_argument("--model", default=None)
    parser.add_argument("--timeout", type=int, default=1800)
    args = parser.parse_args()

    worker = AgentTask(
        CodexCliAgent(model=args.model, timeout_seconds=args.timeout),
        args.instruction,
        args.workspace,
    )
    factory = ProjectFactory(args.run_id, args.project_id)
    factory.add_task(Task("agent-build", "Execute coding-agent task", worker))
    result = factory.run()

    print(json.dumps({
        "status": result.status.value,
        "projectId": result.state.project_id,
        "completedTasks": result.state.completed_tasks,
        "failedTasks": result.state.failed_tasks,
        "blockedReason": result.state.blocked_reason,
        "evidence": [e.__dict__ for e in result.state.evidence],
        "checkpoint": result.state.checkpoint,
    }, indent=2))
    return 0 if result.status.value == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
