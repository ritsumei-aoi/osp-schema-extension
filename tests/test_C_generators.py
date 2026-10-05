import unittest
import json
import os

class TestCGenerators(unittest.TestCase):
    def setUp(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        
    def get_schema(self, n):
        with open(os.path.join(self.data_dir, f"C_{n}_structure.json")) as f:
            return json.load(f)

    def test_dimensions(self):
        for n in [1, 2, 3]:
            schema = self.get_schema(n)
            dim_expected_even = 2*n*n + n + 1
            dim_expected_odd = 4*n
            
            self.assertEqual(len(schema["basis"]["even"]), dim_expected_even)
            self.assertEqual(len(schema["basis"]["odd"]), dim_expected_odd)
            self.assertEqual(schema["algebra"]["dimension"]["even"], dim_expected_even)
            self.assertEqual(schema["algebra"]["dimension"]["odd"], dim_expected_odd)

    def test_parity(self):
        for n in [1, 2, 3]:
            schema = self.get_schema(n)
            
            for even_gen in schema["basis"]["even"]:
                self.assertEqual(schema["parity"][even_gen], 0)
                
            for odd_gen in schema["basis"]["odd"]:
                self.assertEqual(schema["parity"][odd_gen], 1)

    def test_generator_counts(self):
        for n in [1, 2, 3]:
            schema = self.get_schema(n)
            gens = schema["generator_realization"]["realizations"]
            
            self.assertEqual(len(gens), 2*n*n + 5*n + 1)
            
            # Check Cartans
            cartans = [g for g in gens if g.startswith("H_")]
            self.assertEqual(len(cartans), n + 1)

if __name__ == "__main__":
    unittest.main()
