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
    """Real OpenAI Codex CLI adapter for controlled project workspaces.

    Codex is invoked non-interactively with a workspace-write sandbox. The
    workspace must be an existing Git repository. We capture the agent output,
    exit code, and Git changed-file evidence so the Project Factory can make a
    truthful gate decision.
    """

    executable: Sequence[str] = ("codex", "exec")
    timeout_seconds: int = 1800
    sandbox: str = "workspace-write"
    model: str | None = None

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
        self._git(root, "rev-parse", "--show-toplevel")
        before = set(self._git(root, "status", "--porcelain=v1", "--untracked-files=all"))

        command = [*self.executable, "--ephemeral", "--sandbox", self.sandbox, "--json"]
        if self.model:
            command.extend(["--model", self.model])
        command.extend(["-C", str(root), instruction])

        try:
            completed = subprocess.run(
                command,
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
                timeout=self.timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            return AgentResult(
                False,
                "Codex execution timed out",
                sorted(before),
                [str(exc)],
                returncode=124,
            )

        after = set(self._git(root, "status", "--porcelain=v1", "--untracked-files=all"))
        changed = sorted(before.symmetric_difference(after))
        events = []
        for line in completed.stdout.splitlines():
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue

        summary = "Codex completed" if completed.returncode == 0 else "Codex failed"
        evidence = [
            f"exit_code={completed.returncode}",
            f"changed_entries={len(changed)}",
        ]
        if completed.stderr.strip():
            evidence.append(completed.stderr.strip()[-4000:])
        if events:
            evidence.append(f"json_events={len(events)}")

        return AgentResult(
            completed.returncode == 0,
            summary,
            changed,
            evidence,
            completed.returncode,
        )
