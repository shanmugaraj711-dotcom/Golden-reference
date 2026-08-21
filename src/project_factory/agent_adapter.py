from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence


class CodingAgent(Protocol):
    def execute(self, instruction: str, *, workspace: str) -> "AgentResult": ...


@dataclass
class AgentResult:
    success: bool
    summary: str
    changed_files: list[str]
    evidence: list[str]


@dataclass
class CommandCodingAgent:
    """Explicit-command bridge for a real coding-agent CLI.

    The command is configured by the operator/environment, not assembled from
    untrusted prompt text. This keeps the boundary auditable while allowing a
    future Codex/CLI implementation to plug in without changing the factory.
    """

    executable: Sequence[str]

    def execute(self, instruction: str, *, workspace: str) -> AgentResult:
        raise RuntimeError(
            "Coding-agent execution is intentionally disabled until an approved "
            "agent CLI is configured. Use LocalCommandAdapter for deterministic tests."
        )
