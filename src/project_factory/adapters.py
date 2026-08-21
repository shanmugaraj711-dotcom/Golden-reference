from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import subprocess
from typing import Mapping, Sequence


@dataclass
class CommandResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str

    @property
    def passed(self) -> bool:
        return self.returncode == 0


class ProjectAdapter:
    """Boundary between the factory and a concrete project environment."""

    def prepare(self) -> CommandResult:
        raise NotImplementedError

    def build(self) -> CommandResult:
        raise NotImplementedError

    def test(self) -> CommandResult:
        raise NotImplementedError

    def verify(self) -> CommandResult:
        raise NotImplementedError


@dataclass
class LocalCommandAdapter(ProjectAdapter):
    """Safe baseline adapter for a checked-out local project.

    Commands are explicit allowlisted command arrays. The factory never builds
    shell strings from user input, which keeps the adapter suitable for later
    agent integration.
    """

    root: Path
    commands: Mapping[str, Sequence[str]] = field(default_factory=dict)

    def _run(self, name: str) -> CommandResult:
        if name not in self.commands:
            return CommandResult([], 2, "", f"No command configured for {name}")
        command = list(self.commands[name])
        completed = subprocess.run(
            command,
            cwd=self.root,
            capture_output=True,
            text=True,
            check=False,
        )
        return CommandResult(command, completed.returncode, completed.stdout, completed.stderr)

    def prepare(self) -> CommandResult:
        return self._run("prepare")

    def build(self) -> CommandResult:
        return self._run("build")

    def test(self) -> CommandResult:
        return self._run("test")

    def verify(self) -> CommandResult:
        return self._run("verify")
