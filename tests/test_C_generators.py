import json
import unittest
import os

class TestCGenerators(unittest.TestCase):
    def test_generator_counts(self):
        for n in [1, 2, 3]:
            with open(f"data/C_{n}_structure.json", "r") as f:
                schema = json.load(f)
            
            even_dim = 2*n**2 + n + 1
            odd_dim = 4*n
            total_dim = even_dim + odd_dim
            
            self.assertEqual(schema['algebra']['dimension']['even'], even_dim)
            self.assertEqual(schema['algebra']['dimension']['odd'], odd_dim)
            self.assertEqual(schema['algebra']['dimension']['total'], total_dim)
            
            self.assertEqual(len(schema['basis']['even']), even_dim)
            self.assertEqual(len(schema['basis']['odd']), odd_dim)
            
    def test_parities(self):
        for n in [1, 2, 3]:
            with open(f"data/C_{n}_structure.json", "r") as f:
                schema = json.load(f)
            
            parity = schema['parity']
            for g in schema['basis']['even']:
                self.assertEqual(parity[g], 0)
            for g in schema['basis']['odd']:
                self.assertEqual(parity[g], 1)
                
    def test_structure_constants_exist(self):
        for n in [1, 2, 3]:
            with open(f"data/C_{n}_structure.json", "r") as f:
                schema = json.load(f)
            
            sc = schema['structure_constants']
            self.assertTrue(len(sc) > 0)
            
            # just check one bracket's keys
            bracket = sc[0]
            self.assertIn('X', bracket)
            self.assertIn('Y', bracket)
            self.assertIn('Z', bracket)
            self.assertIn('coeff', bracket)
            
if __name__ == '__main__':
    unittest.main()
