from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .model_provider import ModelRequest, ModelResponse, ModelProvider


@dataclass(frozen=True)
class RoutingPolicy:
    """Runtime policy for choosing an AI provider.

    The default is deliberately fail-closed: no paid/external provider can be
    selected unless the operator explicitly raises the spending ceiling.
    """

    prefer_local: bool = True
    allow_external: bool = False
    max_cost: float = 0.0


class ModelRouter:
    """Choose a model provider without coupling the factory to one vendor."""

    def __init__(self, providers: Sequence[ModelProvider], policy: RoutingPolicy | None = None):
        self.providers = list(providers)
        self.policy = policy or RoutingPolicy()
        if self.policy.max_cost < 0:
            raise ValueError("max_cost cannot be negative")

    def complete(self, request: ModelRequest) -> ModelResponse:
        candidates = [p for p in self.providers if p.available()]
        if not candidates:
            raise RuntimeError("No model provider is available")

        if self.policy.prefer_local:
            candidates.sort(key=lambda p: (not p.is_local(), p.estimated_cost(request)))
        else:
            candidates.sort(key=lambda p: p.estimated_cost(request))

        eligible = [p for p in candidates if p.estimated_cost(request) <= self.policy.max_cost]
        if eligible:
            return eligible[0].complete(request)

        # External providers are never a silent escape hatch. They require
        # both explicit opt-in and an explicit non-zero spending ceiling.
        if self.policy.allow_external and self.policy.max_cost > 0:
            external = [
                p for p in candidates
                if not p.is_local() and p.estimated_cost(request) <= self.policy.max_cost
            ]
            if external:
                return external[0].complete(request)

        raise RuntimeError("No provider satisfies the routing policy")
