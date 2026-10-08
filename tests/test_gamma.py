import unittest
import json
import os

class TestCGamma(unittest.TestCase):
    def test_gb_matrix_size(self):
        for n in [1, 2, 3]:
            with open(f"data/C_{n}_gamma.json") as f:
                data = json.load(f)
            params = data["inhomogeneous_deformation"]["gb_matrix"]["parameters"]
            self.assertEqual(len(params), 4 * n)
            self.assertEqual(data["inhomogeneous_deformation"]["gb_matrix"]["dimensions"], [2, 2 * n])

if __name__ == "__main__":
    unittest.main()
