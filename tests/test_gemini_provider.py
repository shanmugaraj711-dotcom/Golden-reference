from project_factory.gemini_provider import GeminiProvider
from project_factory.model_provider import ModelRequest


def test_gemini_provider_is_unavailable_without_secret():
    provider = GeminiProvider(api_key=None)
    assert provider.available() is False
    assert provider.estimated_cost(ModelRequest("code", "build")) == 0.0


def test_gemini_provider_uses_zero_spend_ceiling_by_default():
    provider = GeminiProvider(api_key="fixture-key")
    assert provider.available() is True
    assert provider.is_local() is False
    assert provider.estimated_cost(ModelRequest("code", "build")) == 0.0
