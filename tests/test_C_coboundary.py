import json
import unittest

class TestCCoboundary(unittest.TestCase):
    def test_coboundary_structure(self):
        for n in [1, 2, 3]:
            with open(f"data/C_{n}_coboundary.json", "r") as f:
                schema4 = json.load(f)
                
            self.assertIn('f_map_parameters', schema4)
            self.assertIn('coboundary_deformation', schema4)
            
            # just check one entry
            if schema4['coboundary_deformation']:
                entry = schema4['coboundary_deformation'][0]
                self.assertIn('X', entry)
                self.assertIn('Y', entry)
                self.assertIn('Z', entry)
                self.assertIn('coboundary_coeff', entry)

if __name__ == '__main__':
    unittest.main()
