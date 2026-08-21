from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .agent_adapter import AgentTask, CodingAgent
from .engine import ProjectFactory, RunResult, Task


@dataclass
class FactoryRunner:
    """Compose a coding agent with the Project Factory without bypassing gates."""

    agent: CodingAgent
    workspace: Path
    max_repairs: int = 2

    def run(self, project_id: str, instruction: str, *, run_id: str) -> RunResult:
        factory = ProjectFactory(run_id, project_id, max_repairs=self.max_repairs)
        task = AgentTask(self.agent, instruction, str(self.workspace))
        factory.add_task(Task("coding-agent", "Execute project instruction", task))
        return factory.run()
