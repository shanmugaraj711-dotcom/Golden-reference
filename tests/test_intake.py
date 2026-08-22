import pytest

from project_factory import ProjectIntake, normalize_intake


def test_normalize_customer_intake():
    result = normalize_intake({
        "customer_id": "cust-1",
        "project_name": "Clinic website",
        "brief": "A responsive clinic website",
        "product_type": "web",
        "delivery_mode": "deploy",
        "acceptance_criteria": ["mobile friendly", "contact form"],
    })
    assert isinstance(result, ProjectIntake)
    assert result.customer_id == "cust-1"
    assert result.delivery_mode == "deploy"
    assert result.acceptance_criteria == ("mobile friendly", "contact form")


@pytest.mark.parametrize("field", ["customer_id", "project_name", "brief"])
def test_required_intake_fields(field):
    payload = {
        "customer_id": "cust-1",
        "project_name": "Demo",
        "brief": "Build a site",
    }
    payload[field] = ""
    with pytest.raises(ValueError):
        normalize_intake(payload)


def test_invalid_delivery_mode_is_rejected():
    with pytest.raises(ValueError, match="delivery_mode"):
        normalize_intake({
            "customer_id": "cust-1",
            "project_name": "Demo",
            "brief": "Build a site",
            "delivery_mode": "production",
        })


def test_acceptance_criteria_must_be_a_list():
    with pytest.raises(ValueError, match="acceptance_criteria"):
        normalize_intake({
            "customer_id": "cust-1",
            "project_name": "Demo",
            "brief": "Build a site",
            "acceptance_criteria": "mobile friendly",
        })
