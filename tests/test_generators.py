import unittest
import json
import os

class TestCGenerators(unittest.TestCase):
    def test_generator_counts(self):
        for n in [1, 2, 3]:
            with open(f"data/C_{n}_structure.json") as f:
                data = json.load(f)
            self.assertEqual(len(data["basis"]["even"]), data["algebra"]["dimension"]["even"])
            self.assertEqual(len(data["basis"]["odd"]), data["algebra"]["dimension"]["odd"])
            self.assertEqual(data["algebra"]["dimension"]["total"], data["algebra"]["dimension"]["even"] + data["algebra"]["dimension"]["odd"])

    def test_parity(self):
        for n in [1, 2, 3]:
            with open(f"data/C_{n}_structure.json") as f:
                data = json.load(f)
            for g in data["basis"]["even"]:
                self.assertEqual(data["parity"][g], 0)
            for g in data["basis"]["odd"]:
                self.assertEqual(data["parity"][g], 1)

if __name__ == "__main__":
    unittest.main()
