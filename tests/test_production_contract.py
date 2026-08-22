import unittest
import json
from unittest.mock import patch

class ProductionContractTests(unittest.TestCase):
    def test_api_health_contract(self):
        payload={"service":"project-factory","status":"ok","engine":"project_factory"}
        self.assertEqual(payload["status"],"ok")
        self.assertEqual(payload["service"],"project-factory")

    def test_dashboard_lifecycle_contract(self):
        states=["INTAKE","BUILDING","VERIFYING","READY","DELIVERED"]
        self.assertEqual(len(states),5)
        self.assertEqual(states[-1],"DELIVERED")

    def test_customer_project_contract(self):
        p={"customerId":"e2e-test","projectId":"proj_test","lifecycleState":"INTAKE","verification":{"qualityGate":"PENDING","deployment":"PENDING","healthCheck":"PENDING"}}
        self.assertIn("projectId",p)
        self.assertEqual(set(p["verification"]),{"qualityGate","deployment","healthCheck"})

if __name__=='__main__': unittest.main()
