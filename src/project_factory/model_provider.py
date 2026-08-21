from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class ModelRequest:
    task: str
    instruction: str
    context: dict[str, str] = field(default_factory=dict)


@dataclass
class ModelResponse:
    provider: str
    model: str
    output: str
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost: float | None = None


class ModelProvider(Protocol):
    """Vendor-neutral contract used by the Project Factory."""

    name: str

    def generate(self, request: ModelRequest) -> ModelResponse: ...


class UnconfiguredProvider:
    """Safe placeholder until an approved local or external provider is configured."""

    name = "unconfigured"

    def generate(self, request: ModelRequest) -> ModelResponse:
        raise RuntimeError(
            "No model provider configured. Configure an approved provider before execution."
        )
