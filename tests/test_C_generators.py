import json
import os
import unittest

class TestCGenerators(unittest.TestCase):
    def setUp(self):
        self.schemas = {}
        for n in [1, 2, 3]:
            with open(f"data/C_{n}_structure.json") as f:
                self.schemas[n] = json.load(f)

    def test_generator_counts(self):
        for n in [1, 2, 3]:
            schema = self.schemas[n]
            even = schema["algebra"]["dimension"]["even"]
            odd = schema["algebra"]["dimension"]["odd"]
            self.assertEqual(len(schema["basis"]["even"]), even)
            self.assertEqual(len(schema["basis"]["odd"]), odd)

    def test_parity(self):
        for n in [1, 2, 3]:
            schema = self.schemas[n]
            for gen in schema["basis"]["even"]:
                self.assertEqual(schema["parity"][gen], 0)
            for gen in schema["basis"]["odd"]:
                self.assertEqual(schema["parity"][gen], 1)

    def test_structure_constants_consistency(self):
        for n in [1, 2, 3]:
            schema = self.schemas[n]
            sc = schema["structure_constants"]
            # Just basic checks on the output format
            for term in sc:
                self.assertIn("X", term)
                self.assertIn("Y", term)
                self.assertIn("Z", term)
                self.assertIn("coeff", term)
                self.assertEqual(term["sign_rule"], "graded")

if __name__ == "__main__":
    unittest.main()
