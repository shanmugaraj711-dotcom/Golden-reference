import unittest
from src.project_factory.recovery_executor import next_action

class RecoveryExecutorTests(unittest.TestCase):
    def test_runtime_error(self):
        r=next_action('Function Runtimes must have a valid version')
        self.assertEqual(r['classification'],'invalid_runtime')
        self.assertEqual(r['action'],'validate_vercel_runtime_config')

    def test_dependency_error(self):
        r=next_action('ModuleNotFoundError: No module named firebase_admin')
        self.assertEqual(r['classification'],'missing_dependency')

    def test_unknown_is_quarantined(self):
        r=next_action('something completely unexpected')
        self.assertTrue(r['terminal'])
        self.assertEqual(r['action'],'manual_review')

    def test_attempt_limit(self):
        r=next_action('FUNCTION_INVOCATION_FAILED',4)
        self.assertTrue(r['terminal'])
        self.assertEqual(r['action'],'quarantine')

if __name__ == '__main__': unittest.main()
