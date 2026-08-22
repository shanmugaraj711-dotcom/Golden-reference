from project_factory.model_provider import ModelRequest, ModelResponse
from project_factory.model_router import ModelRouter, RoutingPolicy


class FakeProvider:
    def __init__(self, name, local, cost, available=True):
        self.name = name
        self.local = local
        self.cost = cost
        self._available = available
        self.calls = 0

    def available(self):
        return self._available

    def is_local(self):
        return self.local

    def estimated_cost(self, request):
        return self.cost

    def complete(self, request):
        self.calls += 1
        return ModelResponse(self.name, "fixture", "ok", estimated_cost=self.cost)


def test_local_provider_is_preferred_when_available():
    local = FakeProvider("local", True, 0.0)
    external = FakeProvider("external", False, 0.01)
    router = ModelRouter([external, local], RoutingPolicy(prefer_local=True, max_cost=0.0))
    result = router.complete(ModelRequest("code", "build fixture"))
    assert result.provider == "local"
    assert local.calls == 1
    assert external.calls == 0


def test_external_provider_requires_explicit_opt_in_and_budget():
    external = FakeProvider("external", False, 0.01)
    router = ModelRouter(
        [external],
        RoutingPolicy(prefer_local=False, allow_external=True, max_cost=0.01),
    )
    result = router.complete(ModelRequest("debug", "fix fixture"))
    assert result.provider == "external"
    assert external.calls == 1


def test_zero_spend_policy_never_falls_back_to_paid_external():
    local = FakeProvider("local", True, 0.0, available=False)
    external = FakeProvider("external", False, 0.01)
    router = ModelRouter(
        [local, external],
        RoutingPolicy(prefer_local=True, allow_external=True, max_cost=0.0),
    )
    try:
        router.complete(ModelRequest("debug", "fix fixture"))
        assert False, "zero-spend policy must block paid fallback"
    except RuntimeError as exc:
        assert "routing policy" in str(exc)


def test_router_blocks_when_no_provider_meets_cost_ceiling():
    local = FakeProvider("local", True, 0.01)
    external = FakeProvider("external", False, 0.02)
    router = ModelRouter(
        [local, external],
        RoutingPolicy(prefer_local=True, allow_external=True, max_cost=0.0),
    )
    try:
        router.complete(ModelRequest("code", "build fixture"))
        assert False, "router must not exceed the configured cost ceiling"
    except RuntimeError as exc:
        assert "routing policy" in str(exc)
