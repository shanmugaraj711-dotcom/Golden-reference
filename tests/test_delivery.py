import pytest

from src.project_factory.delivery import DeliveryRequest, plan_delivery


def test_transfer_delivery_requires_handoff_without_factory_maintenance():
    plan = plan_delivery(DeliveryRequest("coffee-site", "transfer", "output.tgz", "none"))
    assert plan.repository_required is True
    assert plan.vercel_required is False
    assert plan.customer_transfer_required is True
    assert plan.handoff_required is True
    assert plan.maintenance_expected is False
    assert plan.decision_deferred is False


def test_deploy_delivery_requires_live_target_and_handoff():
    plan = plan_delivery(DeliveryRequest("coffee-site", "deploy", "output.tgz", "vercel"))
    assert plan.repository_required is True
    assert plan.vercel_required is True
    assert plan.customer_transfer_required is False
    assert plan.handoff_required is True
    assert plan.maintenance_expected is False
    assert plan.decision_deferred is False


def test_managed_delivery_enables_maintenance():
    plan = plan_delivery(DeliveryRequest("coffee-site", "managed", "output.tgz", "vercel"))
    assert plan.repository_required is True
    assert plan.vercel_required is True
    assert plan.customer_transfer_required is False
    assert plan.handoff_required is False
    assert plan.maintenance_expected is True
    assert plan.decision_deferred is False


def test_deploy_without_live_target_is_rejected():
    with pytest.raises(ValueError, match="deploy delivery requires"):
        plan_delivery(DeliveryRequest("coffee-site", "deploy", "output.tgz", "none"))


def test_managed_without_live_target_is_rejected():
    with pytest.raises(ValueError, match="managed delivery requires"):
        plan_delivery(DeliveryRequest("coffee-site", "managed", "output.tgz", "none"))


def test_decide_later_remains_backward_compatible():
    plan = plan_delivery(DeliveryRequest("coffee-site", "decide_later", "output.tgz", "vercel"))
    assert plan.repository_required is True
    assert plan.vercel_required is False
    assert plan.customer_transfer_required is False
    assert plan.handoff_required is False
    assert plan.maintenance_expected is False
    assert plan.decision_deferred is True


def test_delivery_validation():
    with pytest.raises(ValueError):
        plan_delivery(DeliveryRequest("", "transfer", "output.tgz", "vercel"))
    with pytest.raises(ValueError):
        plan_delivery(DeliveryRequest("site", "other", "output.tgz", "vercel"))
    with pytest.raises(ValueError):
        plan_delivery(DeliveryRequest("site", "managed", "", "vercel"))
