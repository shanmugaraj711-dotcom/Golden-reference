import unittest
from unittest.mock import patch

from scripts.phase_e_e2e import check_contracts, check_live


class PhaseEE2ETests(unittest.TestCase):
    def test_all_customer_delivery_contracts_pass(self):
        checks = check_contracts()
        self.assertEqual([c.name for c in checks], [
            "delivery-contract:transfer",
            "delivery-contract:deploy",
            "delivery-contract:managed",
        ])
        self.assertTrue(all(c.passed for c in checks))

    @patch("scripts.phase_e_e2e.fetch_json")
    @patch("scripts.phase_e_e2e.urllib.request.urlopen")
    def test_live_surface_requires_api_project_and_dashboard_evidence(self, urlopen, fetch_json):
        fetch_json.side_effect = [
            (200, {"service": "project-factory", "status": "ok"}),
            (200, {"status": "ok", "project": {
                "projectId": "p1",
                "customerId": "c1",
                "lifecycleState": "READY",
                "verification": {},
                "ownership": {},
                "deliveryEvidence": {},
            }}),
        ]

        class Response:
            def read(self):
                return b"<html><body>PROJECT FACTORY Customer Delivery</body></html>"
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False

        urlopen.return_value = Response()
        checks = check_live("https://example.test", "p1")
        self.assertEqual([c.name for c in checks], ["live-api", "project-read", "dashboard"])
        self.assertTrue(all(c.passed for c in checks))


if __name__ == "__main__":
    unittest.main()
