import json
import os
import unittest
from unittest.mock import patch

from api.projects import normalise

class SecurityAndDeliveryHardeningTests(unittest.TestCase):
    def test_normalise_does_not_expose_secrets(self):
        p=normalise({"projectId":"p","customerId":"c","projectName":"x"})
        text=json.dumps(p).lower()
        self.assertNotIn("private_key",text)
        self.assertNotIn("service_account",text)
        self.assertNotIn("password",text)
        self.assertNotIn("secret",text)

    def test_defaults_are_safe(self):
        p=normalise({"projectId":"p","customerId":"c","projectName":"x"})
        self.assertEqual(p["lifecycleState"],"INTAKE")
        self.assertEqual(p["verification"]["qualityGate"],"PENDING")
        self.assertEqual(p["ownership"]["handoff"],"PENDING")

if __name__ == "__main__":
    unittest.main()
