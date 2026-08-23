import unittest

from src.project_factory.live_run import LiveRun, execute_live


class LiveRunTests(unittest.TestCase):
    def test_full_run_reaches_delivered(self):
        run = execute_live(LiveRun("p1", "r1"), lambda step: (True, f"step {step} verified"))
        self.assertEqual(run.status, "DELIVERED")
        self.assertEqual(run.current_step, 10)
        self.assertEqual(run.evidence[-1]["status"], "DELIVERED")

    def test_bounded_run_stops_at_admin_selected_step(self):
        run = execute_live(LiveRun("p1", "r2", start_step=1, end_step=5), lambda step: (True, "ok"))
        self.assertEqual(run.status, "DELIVERED")
        self.assertEqual(run.current_step, 5)

    def test_provider_failure_blocks_without_fake_success(self):
        run = execute_live(LiveRun("p1", "r3"), lambda step: (step != 4, "provider unavailable" if step == 4 else "ok"))
        self.assertEqual(run.status, "BLOCKED")
        self.assertEqual(run.current_step, 4)
        self.assertEqual(run.evidence[-1]["detail"], "provider unavailable")


if __name__ == "__main__":
    unittest.main()
