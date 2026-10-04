import json
import unittest

class TestCGamma(unittest.TestCase):
    def test_gamma_structure(self):
        for n in [1, 2, 3]:
            with open(f"data/C_{n}_gamma.json", "r") as f:
                schema2 = json.load(f)
                
            gb_params = schema2['gb_matrix']['parameters']
            self.assertEqual(len(gb_params), 4 * n)
            
            gamma_out = schema2['inhomogeneous_deformation']
            self.assertTrue(len(gamma_out) > 0)
            
            # just check one entry
            entry = gamma_out[0]
            self.assertIn('X', entry)
            self.assertIn('Y', entry)
            self.assertIn('Z', entry)
            self.assertIn('gamma_coeff', entry)
            
if __name__ == '__main__':
    unittest.main()
