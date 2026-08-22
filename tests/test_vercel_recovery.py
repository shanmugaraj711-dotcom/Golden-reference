import unittest
from src.project_factory.vercel_recovery import classify_failure, recovery_event

class VercelRecoveryTests(unittest.TestCase):
    def test_runtime_failure(self):
        p=classify_failure('Error: Function Runtimes must have a valid version, for example now-php@1.0.0.')
        self.assertEqual(p.category,'runtime_config'); self.assertTrue(p.retryable)

    def test_missing_dependency(self):
        p=classify_failure('ModuleNotFoundError: No module named firebase_admin')
        self.assertEqual(p.category,'missing_dependency'); self.assertTrue(p.retryable)

    def test_import_failure(self):
        p=classify_failure('could not import "api/index.py": ImportError')
        self.assertEqual(p.category,'function_import')

    def test_unknown_failure_is_quarantined(self):
        p=classify_failure('database exploded in an unknown way')
        self.assertEqual(p.category,'unknown'); self.assertFalse(p.retryable)

    def test_event_has_attempt(self):
        e=recovery_event('FUNCTION_INVOCATION_FAILED',3)
        self.assertEqual(e['attempt'],3); self.assertEqual(e['category'],'function_invocation')

if __name__ == '__main__': unittest.main()
