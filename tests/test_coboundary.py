import unittest
import json
import os

class TestCCoboundary(unittest.TestCase):
    def test_coboundary_layer(self):
        for n in [1, 2, 3]:
            with open(f"data/C_{n}_coboundary.json") as f:
                data = json.load(f)
            self.assertEqual(data["layer"], "Schema 4")
            self.assertIn("coboundary_structure", data)

if __name__ == "__main__":
    unittest.main()
