import unittest

from src.project_factory.run_manager import RunStage, new_run


class FactoryRunTests(unittest.TestCase):
    def test_run_survives_block_and_resumes_from_checkpoint(self):
        run = new_run("customer-1", "project-1")
        run.checkpoint(RunStage.BUILD)
        run.checkpoint(RunStage.TEST)
        run.block("Vercel authorization required")
        self.assertEqual(run.status, "BLOCKED")
        self.assertEqual(run.stage, RunStage.BLOCKED)
        run.resume()
        self.assertEqual(run.status, "RUNNING")
        self.assertEqual(run.stage, RunStage.TEST)
        self.assertEqual(run.completed_stages, ["BUILD", "TEST"])

    def test_retry_budget_fail_closes(self):
        run = new_run("customer-1", "project-1")
        self.assertTrue(run.attempt(RunStage.BUILD, 2))
        self.assertTrue(run.attempt(RunStage.BUILD, 2))
        self.assertFalse(run.attempt(RunStage.BUILD, 2))
        self.assertEqual(run.status, "BLOCKED")

    def test_complete_requires_real_delivery_evidence_stages(self):
        run = new_run("customer-1", "project-1")
        with self.assertRaises(ValueError):
            run.checkpoint(RunStage.COMPLETE)
        for stage in (RunStage.REPOSITORY, RunStage.DEPLOY, RunStage.HEALTH, RunStage.EVIDENCE, RunStage.HANDOFF):
            run.checkpoint(stage)
        run.checkpoint(RunStage.COMPLETE)
        self.assertEqual(run.status, "COMPLETE")


if __name__ == "__main__":
    unittest.main()
