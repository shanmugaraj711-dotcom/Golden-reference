import unittest

from src.project_factory.customer_workflow import CustomerWorkflow, WorkflowStep, step_slice


class CustomerWorkflowTests(unittest.TestCase):
    def test_default_customer_run_is_full_ten_steps(self):
        run = CustomerWorkflow("p1").start("Build a restaurant app")
        self.assertEqual(run.started_at_step, 1)
        self.assertEqual(run.end_at_step, 10)
        self.assertEqual(len(step_slice(run.started_at_step, run.end_at_step)), 10)

    def test_admin_can_run_only_steps_one_to_five(self):
        run = CustomerWorkflow("p1").start("Build a restaurant app", start_step=1, end_step=5)
        self.assertEqual(step_slice(run.started_at_step, run.end_at_step), (
            WorkflowStep.INTAKE, WorkflowStep.REQUIREMENTS, WorkflowStep.PLAN,
            WorkflowStep.BUILD, WorkflowStep.TEST,
        ))

    def test_customer_feedback_creates_new_version_from_selected_step(self):
        flow = CustomerWorkflow("p1")
        first = flow.start("Build a restaurant app")
        second = flow.revise("Change the dashboard UI", start_step=4, end_step=10)
        self.assertEqual(first.version, 1)
        self.assertEqual(second.version, 2)
        self.assertEqual(second.started_at_step, 4)
        self.assertEqual(second.end_at_step, 10)
        self.assertEqual(len(flow.history), 2)

    def test_admin_controls_pause_resume_and_approval(self):
        flow = CustomerWorkflow("p1")
        flow.start("Build an app")
        flow.pause("founder review")
        self.assertEqual(flow.active.status, "paused")
        flow.resume()
        self.assertEqual(flow.active.status, "running")
        flow.approve()
        self.assertEqual(flow.active.status, "approved")

    def test_invalid_stage_range_is_rejected(self):
        with self.assertRaises(ValueError):
            CustomerWorkflow("p1").start("Build", start_step=6, end_step=5)


if __name__ == "__main__":
    unittest.main()
