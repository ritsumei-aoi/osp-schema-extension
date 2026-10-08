import unittest
from pathlib import Path

from src.search_C_triviality import analyze_rank


class SearchCTrivialityTests(unittest.TestCase):
    def test_every_gb_parameter_has_an_uncancellable_central_witness(self):
        data_dir = Path(__file__).resolve().parents[1] / "data"
        for n in (1, 2, 3):
            with self.subTest(n=n):
                result = analyze_rank(n, data_dir)
                self.assertEqual(result["parameter_count"], 4 * n)
                self.assertEqual(result["individual_K_obstructions"], 4 * n)
                self.assertTrue(result["uniform_plus_one_nontrivial"])
                self.assertTrue(result["zero_assignment_trivial"])
                self.assertEqual(
                    len(result["triviality_conditions"]),
                    4 * n,
                )


if __name__ == "__main__":
    unittest.main()
