import pytest

from src.project_factory.delivery import DeliveryRequest, plan_delivery


def test_customer_delivery_requires_transfer_and_vercel():
    plan = plan_delivery(DeliveryRequest("coffee-site", "customer", "output.tgz", "vercel"))
    assert plan.repository_required is True
    assert plan.vercel_required is True
    assert plan.customer_transfer_required is True


def test_managed_delivery_keeps_transfer_off():
    plan = plan_delivery(DeliveryRequest("coffee-site", "managed", "output.tgz", "vercel"))
    assert plan.repository_required is True
    assert plan.vercel_required is True
    assert plan.customer_transfer_required is False


def test_delivery_validation():
    with pytest.raises(ValueError):
        plan_delivery(DeliveryRequest("", "customer", "output.tgz", "vercel"))
    with pytest.raises(ValueError):
        plan_delivery(DeliveryRequest("site", "other", "output.tgz", "vercel"))
