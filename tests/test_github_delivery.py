import pytest

from src.project_factory.delivery import DeliveryRequest, plan_delivery
from src.project_factory.github_delivery import plan_github_delivery


def base_plan():
    return plan_delivery(DeliveryRequest("coffee-site", "customer", "output.tgz", "vercel"))


def test_github_delivery_uses_non_default_branch():
    result = plan_github_delivery(base_plan(), "customer/site", "factory/coffee-site")
    assert result.repository == "customer/site"
    assert result.branch == "factory/coffee-site"
    assert result.create_pull_request is True


def test_github_delivery_rejects_default_branch():
    with pytest.raises(ValueError):
        plan_github_delivery(base_plan(), "customer/site", "main")


def test_github_delivery_rejects_bad_repository():
    with pytest.raises(ValueError):
        plan_github_delivery(base_plan(), "not-a-repo")
