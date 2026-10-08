import unittest
import json
import os

class TestCEvaluated(unittest.TestCase):
    def test_evaluated_assignment(self):
        for n in [1, 2, 3]:
            with open(f"data/C_{n}_evaluated.json") as f:
                data = json.load(f)
            assignment = data["evaluated_deformation"]["gb_matrix_assignment"]
            self.assertEqual(len(assignment), 4 * n)
            for k, v in assignment.items():
                self.assertEqual(v, 1)

if __name__ == "__main__":
    unittest.main()
