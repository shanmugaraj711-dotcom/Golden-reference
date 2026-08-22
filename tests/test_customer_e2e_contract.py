import unittest
from unittest.mock import patch

from api.projects import authorize, normalise, STATES, VK, OK

class FakeHeader:
    def __init__(self, token=""):
        self.headers={"Authorization": token} if token else {}

class CustomerE2EContractTests(unittest.TestCase):
    def test_customer_can_access_own_project(self):
        project=normalise({"projectId":"p1","customerId":"customer-a","projectName":"A"})
        authorize({"uid":"u-a","customerId":"customer-a","internal":False}, project)

    def test_customer_is_denied_other_customer_project(self):
        project=normalise({"projectId":"p2","customerId":"customer-b","projectName":"B"})
        with self.assertRaises(PermissionError):
            authorize({"uid":"u-a","customerId":"customer-a","internal":False}, project)

    def test_internal_operator_can_access_project(self):
        project=normalise({"projectId":"p3","customerId":"customer-b","projectName":"B"})
        authorize({"uid":"internal","customerId":"*","internal":True}, project)

    def test_delivery_contract_has_all_required_gates(self):
        self.assertEqual(STATES, ["INTAKE","BUILDING","VERIFYING","READY","DELIVERED"])
        self.assertEqual(VK, ("qualityGate","deployment","healthCheck"))
        self.assertEqual(OK, ("repository","hosting","handoff"))

    def test_customer_data_model_has_approval_and_change_request_history(self):
        p=normalise({"projectId":"p4","customerId":"customer-a","projectName":"A"})
        self.assertEqual(p["approvals"], [])
        self.assertEqual(p["changeRequests"], [])
        self.assertEqual(p["lifecycleHistory"], [])
        self.assertEqual(p["deliveryEvidence"], {})

if __name__ == "__main__":
    unittest.main()
