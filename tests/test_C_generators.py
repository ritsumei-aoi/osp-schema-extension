import unittest
import json
import os

class TestCGenerators(unittest.TestCase):
    def test_generator_counts(self):
        for n in [1, 2, 3]:
            with open(f"data/C_{n}_structure.json", "r") as f:
                data = json.load(f)
            
            even_count = data['algebra']['dimension']['even']
            odd_count = data['algebra']['dimension']['odd']
            
            self.assertEqual(len(data['basis']['even']), even_count)
            self.assertEqual(len(data['basis']['odd']), odd_count)
            
            total = even_count + odd_count
            self.assertEqual(len(data['generator_realization']['realizations']), total)

    def test_parity(self):
        for n in [1, 2, 3]:
            with open(f"data/C_{n}_structure.json", "r") as f:
                data = json.load(f)
            
            for g in data['basis']['even']:
                self.assertEqual(data['parity'][g], 0)
                
            for g in data['basis']['odd']:
                self.assertEqual(data['parity'][g], 1)

    def test_schema_compliance(self):
        for n in [1, 2, 3]:
            with open(f"data/C_{n}_structure.json", "r") as f:
                data = json.load(f)
            
            self.assertEqual(data['schema_version'], "5.0")
            self.assertEqual(data['algebra']['family'], "C")
            self.assertEqual(data['algebra']['m'], 1)
            self.assertEqual(data['algebra']['n'], n)
            self.assertIn("fermions", data['oscillator_generators'])
            self.assertNotIn("supplementary_fermion", data['oscillator_generators'])

if __name__ == '__main__':
    unittest.main()
