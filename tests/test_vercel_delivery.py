import pytest

from src.project_factory.vercel_delivery import VercelDeploymentTarget, validate_vercel_target


def test_vercel_target_accepts_https_url():
    result = validate_vercel_target(VercelDeploymentTarget("coffee-site", "https://coffee-site.vercel.app"))
    assert result.project_name == "coffee-site"


def test_vercel_target_rejects_non_https():
    with pytest.raises(ValueError):
        validate_vercel_target(VercelDeploymentTarget("coffee-site", "http://coffee-site.vercel.app"))
