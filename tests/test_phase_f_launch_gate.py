import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.phase_f_launch_gate import REQUIRED, main


class PhaseFLaunchGateTests(unittest.TestCase):
    def test_complete_evidence_is_ready(self):
        evidence = {key: True for key in REQUIRED}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "evidence.json"
            path.write_text(json.dumps(evidence), encoding="utf-8")
            with patch("sys.argv", ["phase_f_launch_gate", "--evidence", str(path)]):
                self.assertEqual(main(), 0)

    def test_missing_evidence_fails_closed(self):
        evidence = {key: False for key in REQUIRED}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "evidence.json"
            path.write_text(json.dumps(evidence), encoding="utf-8")
            with patch("sys.argv", ["phase_f_launch_gate", "--evidence", str(path)]):
                self.assertEqual(main(), 1)


if __name__ == "__main__":
    unittest.main()
