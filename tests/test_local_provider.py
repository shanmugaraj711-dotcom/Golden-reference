from project_factory.local_provider import OpenAICompatibleLocalProvider
from project_factory.model_provider import ModelRequest


def test_local_provider_is_zero_api_cost_and_local():
    provider = OpenAICompatibleLocalProvider(model="fixture")
    assert provider.is_local() is True
    assert provider.estimated_cost(ModelRequest("code", "build")) == 0.0


def test_local_provider_reports_unavailable_without_runtime():
    provider = OpenAICompatibleLocalProvider(endpoint="http://127.0.0.1:1/v1/chat/completions")
    assert provider.available() is False
