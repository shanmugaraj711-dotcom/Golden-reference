import os
import unittest

from api.factory-auth import issue_session


class FounderAuthTests(unittest.TestCase):
    def test_session_requires_secret(self):
        os.environ.pop("FOUNDER_SESSION_SECRET", None)
        with self.assertRaises(RuntimeError):
            issue_session("founder")

    def test_session_is_short_lived_and_signed(self):
        os.environ["FOUNDER_SESSION_SECRET"] = "test-secret"
        token = issue_session("founder")
        self.assertEqual(token.count("."), 1)
        self.assertGreater(len(token), 40)


if __name__ == "__main__":
    unittest.main()
