import unittest
from src.project_factory.recovery_evidence import event, append

class RecoveryEvidenceTests(unittest.TestCase):
    def test_event_is_bounded(self):
        e=event('FAILED','invalid_runtime','validate_vercel_runtime_config',1,'x'*5000)
        self.assertEqual(e['stage'],'FAILED')
        self.assertLessEqual(len(e['message']),1000)

    def test_history_is_bounded(self):
        h=[]
        for i in range(60): h=append(h,event('VERIFYING','x','y',i))
        self.assertEqual(len(h),50)
        self.assertEqual(h[0]['attempt'],10)

if __name__=='__main__': unittest.main()
