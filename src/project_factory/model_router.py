from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .model_provider import ModelRequest, ModelResponse, ModelProvider


@dataclass(frozen=True)
class RoutingPolicy:
    prefer_local: bool = True
    allow_external: bool = True
    max_cost: float = 0.0


class ModelRouter:
    """Choose a model provider without coupling the factory to one vendor."""

    def __init__(self, providers: Sequence[ModelProvider], policy: RoutingPolicy | None = None):
        self.providers = list(providers)
        self.policy = policy or RoutingPolicy()

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

        if self.policy.allow_external:
            external = [p for p in candidates if not p.is_local()]
            if external:
                return external[0].complete(request)

        raise RuntimeError("No provider satisfies the routing policy")
