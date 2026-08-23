import unittest

from src.project_factory.customer_automation import CustomerAutomation, CustomerRequest, CustomerStage


class CustomerAutomationTests(unittest.TestCase):
    def _caps(self, managed=False):
        calls = []

        def cap(name, result=(True, "ok")):
            def run():
                calls.append(name)
                return result
            return run

        caps = {
            CustomerStage.INTAKE: cap("intake"),
            CustomerStage.AUTH: cap("auth"),
            CustomerStage.BUILD: cap("build"),
            CustomerStage.QUALITY: cap("quality"),
            CustomerStage.REPOSITORY: cap("repository"),
            CustomerStage.DEPLOY: cap("deploy", (True, "deployed", "https://example.test")),
            CustomerStage.HEALTH: cap("health"),
            CustomerStage.EVIDENCE: cap("evidence"),
            CustomerStage.HANDOFF: cap("handoff"),
        }
        if managed:
            caps[CustomerStage.MANAGED] = cap("managed")
        return caps, calls

    def test_deploy_runs_end_to_end_and_records_url(self):
        request = CustomerRequest("r1", "Demo", "deploy", "owner/demo")
        automation = CustomerAutomation(request)
        caps, calls = self._caps()
        result = automation.execute(caps)
        self.assertEqual(result.status, "complete")
        self.assertEqual(result.stage, CustomerStage.COMPLETE)
        self.assertEqual(result.deployment_url, "https://example.test")
        self.assertIn("health", calls)

    def test_managed_requires_managed_capability(self):
        request = CustomerRequest("r2", "Demo", "managed", "owner/demo")
        automation = CustomerAutomation(request)
        caps, _ = self._caps(managed=False)
        result = automation.execute(caps)
        self.assertEqual(result.status, "blocked")
        self.assertIn("managed", result.blocked_reason)

    def test_missing_capability_fails_closed(self):
        request = CustomerRequest("r3", "Demo", "deploy", "owner/demo")
        automation = CustomerAutomation(request)
        caps, _ = self._caps()
        del caps[CustomerStage.QUALITY]
        result = automation.execute(caps)
        self.assertEqual(result.status, "blocked")
        self.assertEqual(result.stage, CustomerStage.BLOCKED)

    def test_transfer_stops_before_deploy_and_health(self):
        request = CustomerRequest("r4", "Demo", "transfer", "owner/demo")
        automation = CustomerAutomation(request)
        caps, calls = self._caps()
        result = automation.execute(caps)
        self.assertEqual(result.status, "complete")
        self.assertNotIn("deploy", calls)
        self.assertNotIn("health", calls)


if __name__ == "__main__":
    unittest.main()
