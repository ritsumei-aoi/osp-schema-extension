import json
import sys
import unittest
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from C_evaluate import (  # noqa: E402
    build_evaluated_schema,
    verify_evaluated_schema,
)


ROOT = Path(__file__).resolve().parents[1]


class CEvaluationTests(unittest.TestCase):
    def _load_gamma(self, rank):
        path = ROOT / "data" / f"C_{rank}_gamma.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def test_uniform_positive_profile_matches_schema_2_for_all_ranks(self):
        for rank in (1, 2, 3):
            with self.subTest(rank=rank):
                gamma = self._load_gamma(rank)
                evaluated = build_evaluated_schema(
                    gamma, generation_date="2026-10-10"
                )
                assignment = evaluated["gb_assignment"]["parameters"]
                self.assertEqual(len(assignment), 4 * rank)
                self.assertEqual(set(assignment.values()), {"1"})

                expected = defaultdict(Fraction)
                for record in gamma["gamma_constants"]:
                    key = (record["X"], record["Y"], record["Z"])
                    for term in record["coeff"]:
                        expected[key] += Fraction(term["scalar"])
                expected = {
                    key: value
                    for key, value in expected.items()
                    if value
                }
                actual = {
                    (record["X"], record["Y"], record["Z"]): Fraction(
                        record["coeff"]
                    )
                    for record in evaluated["evaluated_constants"]
                }
                self.assertEqual(actual, expected)
                self.assertEqual(
                    verify_evaluated_schema(gamma, evaluated), len(expected)
                )

    def test_verifier_rejects_inconsistent_evaluated_coefficient(self):
        gamma = self._load_gamma(1)
        evaluated = build_evaluated_schema(gamma, generation_date="2026-10-10")
        evaluated["evaluated_constants"][0]["coeff"] = "999"
        with self.assertRaisesRegex(ValueError, "does not match evaluation"):
            verify_evaluated_schema(gamma, evaluated)


if __name__ == "__main__":
    unittest.main()
