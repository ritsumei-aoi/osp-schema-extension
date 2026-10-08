import json
import unittest
from fractions import Fraction
from pathlib import Path

from src.evaluate_C_gamma import evaluate_schema


class EvaluateCGammaTests(unittest.TestCase):
    def test_uniform_assignment_matches_schema2(self):
        data_dir = Path(__file__).resolve().parents[1] / "data"
        for n in (1, 2, 3):
            with self.subTest(n=n):
                structure = json.loads(
                    (data_dir / f"C_{n}_structure.json").read_text()
                )
                gamma = json.loads((data_dir / f"C_{n}_gamma.json").read_text())
                evaluated = evaluate_schema(structure, gamma)
                stored = json.loads((data_dir / f"C_{n}_evaluated.json").read_text())
                self.assertEqual(stored["evaluation"], evaluated["evaluation"])
                self.assertEqual(
                    stored["evaluated_structure_constants"],
                    evaluated["evaluated_structure_constants"],
                )
                assignment = evaluated["evaluation"]["parameter_assignment"]
                self.assertEqual(len(assignment), 4 * n)
                self.assertEqual(set(assignment.values()), {1})
                rows = {
                    (row["X"], row["Y"], row["Z"]): row
                    for row in evaluated["evaluated_structure_constants"]
                }
                for row in gamma["inhomogeneous_deformation"]["gamma_coefficients"]:
                    key = (row["X"], row["Y"], row["Z"])
                    expected = sum(
                        (Fraction(term["coeff"]) * assignment[term["parameter"]]
                         for term in row["terms"]),
                        Fraction(),
                    )
                    self.assertEqual(
                        Fraction(rows[key]["evaluated_gamma_coeff"]),
                        expected,
                    )
                for row in structure["structure_constants"]:
                    key = (row["X"], row["Y"], row["Z"])
                    self.assertEqual(
                        Fraction(rows[key]["base_coeff"]),
                        Fraction(row["coeff"]),
                    )


if __name__ == "__main__":
    unittest.main()
