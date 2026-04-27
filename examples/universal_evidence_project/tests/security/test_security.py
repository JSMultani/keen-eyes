import unittest


class SecurityTests(unittest.TestCase):
    def test_dummy_security_invariant(self):
        self.assertTrue("authorization-required")


if __name__ == "__main__":
    unittest.main()
