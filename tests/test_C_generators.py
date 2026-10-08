import unittest
import json

class TestCGenerators(unittest.TestCase):
    def test_schema_properties(self):
        for n in [1, 2, 3]:
            with open(f"data/C_{n}_structure.json") as f:
                schema = json.load(f)
                
            # Parity check
            even_count = len(schema["basis"]["even"])
            odd_count = len(schema["basis"]["odd"])
            
            # Expected formulas
            expected_even = 2*n**2 + n + 1
            expected_odd = 4*n
            
            self.assertEqual(even_count, expected_even)
            self.assertEqual(odd_count, expected_odd)
            self.assertEqual(schema["algebra"]["dimension"]["total"], even_count + odd_count)

if __name__ == "__main__":
    unittest.main()
