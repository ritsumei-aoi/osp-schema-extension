import json
import unittest

class TestCEvaluated(unittest.TestCase):
    def test_evaluated_structure(self):
        for n in [1, 2, 3]:
            with open(f"data/C_{n}_evaluated.json", "r") as f:
                schema3 = json.load(f)
                
            self.assertIn('evaluation_assignment', schema3)
            self.assertIn('evaluated_deformation', schema3)
            
            # just check one entry
            if schema3['evaluated_deformation']:
                entry = schema3['evaluated_deformation'][0]
                self.assertIn('X', entry)
                self.assertIn('Y', entry)
                self.assertIn('Z', entry)
                self.assertIn('gamma_coeff', entry)
                # It should be a constant string
                self.assertTrue(entry['gamma_coeff'].lstrip('-').replace('/', '', 1).isdigit())

if __name__ == '__main__':
    unittest.main()
