import unittest

from src.project_factory.lifecycle_worker import LifecycleWorker, StageResult


class LifecycleWorkerTests(unittest.TestCase):
    def test_worker_advances_and_persists_each_stage(self):
        project = {"projectId": "p1", "lifecycleState": "INTAKE", "deliveryEvidence": {}}
        saved = []

        def load(_):
            return project

        def persist(_, value):
            project.update(value)
            saved.append(value["lifecycleState"])

        adapters = {
            "BUILDING": lambda _: StageResult(True, {"build": "passed"}),
            "VERIFYING": lambda _: StageResult(True, {"quality": "passed", "deployment": "passed", "health": "passed"}),
            "READY": lambda _: StageResult(True, {"ready": True}),
            "DELIVERED": lambda _: StageResult(True, {"handoff": "passed"}),
        }
        result = LifecycleWorker(load, persist, adapters).advance("p1")
        self.assertEqual(result["lifecycleState"], "DELIVERED")
        self.assertEqual(saved, ["INTAKE", "BUILDING", "VERIFYING", "READY", "DELIVERED"])

    def test_worker_blocks_when_provider_fails_and_does_not_advance(self):
        project = {"projectId": "p2", "lifecycleState": "INTAKE", "deliveryEvidence": {}}
        saved = []

        def persist(_, value):
            project.update(value)
            saved.append(dict(value))

        adapters = {"BUILDING": lambda _: StageResult(False, {}, "provider unavailable")}
        result = LifecycleWorker(lambda _: project, persist, adapters).advance("p2")
        self.assertEqual(result["lifecycleState"], "INTAKE")
        self.assertEqual(result["factoryStatus"], "BLOCKED")
        self.assertIn("provider unavailable", result["factoryBlocker"])

    def test_bounded_run_stops_at_requested_stage(self):
        project = {"projectId": "p3", "lifecycleState": "INTAKE", "deliveryEvidence": {}}
        saved = []
        adapters = {stage: (lambda _: StageResult(True, {stage: "passed"})) for stage in ("BUILDING", "VERIFYING", "READY", "DELIVERED")}
        result = LifecycleWorker(lambda _: project, lambda _, v: (project.update(v), saved.append(v["lifecycleState"])), adapters).advance("p3", "VERIFYING")
        self.assertEqual(result["lifecycleState"], "VERIFYING")
        self.assertEqual(saved[-1], "VERIFYING")


if __name__ == "__main__":
    unittest.main()
