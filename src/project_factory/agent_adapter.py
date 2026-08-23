from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import subprocess
from typing import Protocol, Sequence


class CodingAgent(Protocol):
    def execute(self, instruction: str, *, workspace: str) -> "AgentResult": ...


@dataclass
class AgentResult:
    success: bool
    summary: str
    changed_files: list[str]
    evidence: list[str]
    returncode: int = 0


@dataclass
class CommandCodingAgent:
    """Explicit-command bridge for an approved coding-agent CLI."""

    executable: Sequence[str]

    def execute(self, instruction: str, *, workspace: str) -> AgentResult:
        raise RuntimeError(
            "Coding-agent execution is intentionally disabled until an approved "
            "agent CLI is configured. Use CodexCliAgent or LocalCommandAdapter."
        )


@dataclass
class CodexCliAgent:
    """Real OpenAI Codex CLI adapter for controlled project workspaces."""

    executable: Sequence[str] = ("codex", "exec")
    timeout_seconds: int = 1800
    sandbox: str = "workspace-write"
    model: str | None = None

    def __post_init__(self) -> None:
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if self.timeout_seconds > 3600:
            raise ValueError("timeout_seconds exceeds the one-hour safety limit")
        if self.sandbox != "workspace-write":
            raise ValueError("CodexCliAgent only permits the workspace-write sandbox")
        if not self.executable:
            raise ValueError("Codex executable must not be empty")

    def _git(self, workspace: Path, *args: str) -> list[str]:
        result = subprocess.run(
            ["git", *args], cwd=workspace, capture_output=True, text=True, check=False
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "git command failed")
        return result.stdout.splitlines()

    def execute(self, instruction: str, *, workspace: str) -> AgentResult:
        root = Path(workspace).resolve()
        if not root.is_dir():
            raise ValueError(f"Workspace does not exist: {root}")
        if not instruction.strip():
            raise ValueError("Agent instruction must not be empty")
        top_level = Path(self._git(root, "rev-parse", "--show-toplevel")[0]).resolve()
        if top_level != root:
            raise ValueError("Workspace must be the Git repository root")
        before = set(self._git(root, "status", "--porcelain=v1", "--untracked-files=all"))

        command = [*self.executable, "--ephemeral", "--sandbox", self.sandbox, "--json"]
        if self.model:
            command.extend(["--model", self.model])
        command.extend(["-C", str(root), instruction])

        try:
            completed = subprocess.run(
                command, cwd=root, capture_output=True, text=True,
                check=False, timeout=self.timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            return AgentResult(False, "Codex execution timed out", sorted(before), [str(exc)], 124)

        after = set(self._git(root, "status", "--porcelain=v1", "--untracked-files=all"))
        changed = sorted(before.symmetric_difference(after))
        events = []
        for line in completed.stdout.splitlines():
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue

        summary = "Codex completed" if completed.returncode == 0 else "Codex failed"
        evidence = [f"exit_code={completed.returncode}", f"changed_entries={len(changed)}"]
        if completed.stderr.strip():
            evidence.append(completed.stderr.strip()[-4000:])
        if events:
            evidence.append(f"json_events={len(events)}")
        return AgentResult(completed.returncode == 0, summary, changed, evidence, completed.returncode)


@dataclass
class AgentTask:
    """Callable task bridge: ProjectFactory -> CodingAgent -> evidence."""

    agent: CodingAgent
    instruction: str
    workspace: str
    last_result: AgentResult | None = None

    def __call__(self) -> bool:
        self.last_result = self.agent.execute(self.instruction, workspace=self.workspace)
        return self.last_result.success
