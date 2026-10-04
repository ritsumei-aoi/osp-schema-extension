import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from C_generators import get_generators, get_parity, generate_schema

class TestCGenerators(unittest.TestCase):
    def test_dimensions(self):
        for n in [1, 2, 3]:
            gens = get_generators(n)
            even = sum(1 for g in gens.values() if get_parity(g) == 0)
            odd = sum(1 for g in gens.values() if get_parity(g) == 1)
            
            self.assertEqual(even, 2*n*n + n + 1)
            self.assertEqual(odd, 4*n)
            self.assertEqual(even + odd, 2*n*n + 5*n + 1)
            
    def test_schema_generation(self):
        # Just test n=1 generation
        schema = generate_schema(1)
        self.assertEqual(schema["algebra"]["family"], "C")
        self.assertTrue("fermions" in schema["oscillator_generators"])
        self.assertTrue("kappa" in schema["central_elements"])
        self.assertEqual(len(schema["basis"]["even"]), 4)
        self.assertEqual(len(schema["basis"]["odd"]), 4)
        
if __name__ == "__main__":
    unittest.main()
