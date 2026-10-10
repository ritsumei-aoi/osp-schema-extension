import unittest
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from C_generators import get_generators

class TestCGenerators(unittest.TestCase):
    def test_dimensions(self):
        for n in [1, 2, 3]:
            gens, parities = get_generators(n)
            
            even_count = sum(1 for g in gens if parities[g] == 0)
            odd_count = sum(1 for g in gens if parities[g] == 1)
            
            self.assertEqual(even_count, 2*n*n + n + 1)
            self.assertEqual(odd_count, 4*n)
            self.assertEqual(len(gens), 2*n*n + 5*n + 1)

    def test_schema_validity(self):
        for n in [1, 2, 3]:
            path = f'data/C_{n}_structure.json'
            self.assertTrue(os.path.exists(path))
            with open(path, 'r') as f:
                data = json.load(f)
                
            self.assertEqual(data["schema_version"], "5.0")
            self.assertEqual(data["algebra"]["family"], "C")
            self.assertEqual(data["algebra"]["n"], n)
            self.assertIn("fermionic_anticommutators", data["oscillator_relations"])
            self.assertIn("central_elements", data)

if __name__ == '__main__':
    unittest.main()
