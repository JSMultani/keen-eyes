import unittest


class DemoTests(unittest.TestCase):
    def test_dummy_business_rule(self):
        self.assertEqual("keen".upper(), "KEEN")


if __name__ == "__main__":
    unittest.main()

