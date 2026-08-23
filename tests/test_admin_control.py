import unittest

from src.project_factory.admin_control import AdminCommand, dashboard_state, execute_command
from src.project_factory.customer_workflow import CustomerWorkflow


class AdminControlTests(unittest.TestCase):
    def test_admin_starts_bounded_range(self):
        flow = CustomerWorkflow("p1")
        run = execute_command(flow, AdminCommand(action="start", start_step=1, end_step=5, instruction="Build app"))
        self.assertEqual((run.started_at_step, run.end_at_step), (1, 5))

    def test_admin_targeted_revision(self):
        flow = CustomerWorkflow("p1")
        execute_command(flow, AdminCommand(action="start", instruction="Build app"))
        run = execute_command(flow, AdminCommand(action="revise", start_step=4, end_step=10, instruction="Change dashboard"))
        self.assertEqual(run.version, 2)
        self.assertEqual(run.started_at_step, 4)

    def test_dashboard_exposes_control_state(self):
        flow = CustomerWorkflow("p1")
        execute_command(flow, AdminCommand(action="start", instruction="Build app"))
        state = dashboard_state(flow)
        self.assertEqual(state["stageRange"], {"min": 1, "max": 10})
        self.assertIn("revise", state["controls"])
        self.assertEqual(state["currentVersion"], 1)


if __name__ == "__main__":
    unittest.main()
