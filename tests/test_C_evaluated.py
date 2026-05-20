from __future__ import annotations

import sys
import unittest
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import C_evaluated as cevaluated
import C_gamma as cgamma


class CEvaluatedTestCase(unittest.TestCase):
    def test_gb_zero_profile_covers_all_parameters_for_n_1_2_3(self) -> None:
        for n in (1, 2, 3):
            profile = cevaluated.build_profile_assignments(n, "gb_zero")
            self.assertEqual(list(profile["gb_values"].keys()), cgamma.gb_labels_in_order(n))
            self.assertTrue(all(value == Fraction(0) for value in profile["gb_values"].values()))

    def test_zero_profile_annuls_known_gamma_entry(self) -> None:
        gamma_schema = cevaluated.load_gamma_schema(1)
        profile = cevaluated.build_profile_assignments(1, "gb_zero")
        entry = gamma_schema["inhomogeneous_deformation"]["gamma_matrix"][0]
        self.assertEqual(
            cevaluated.evaluate_linear_coefficient(entry["coeff"], profile["gb_values"]),
            Fraction(0),
        )

    def test_evaluated_schema_recovers_schema1_for_gb_zero(self) -> None:
        for n in (1, 2, 3):
            schema = cevaluated.build_evaluated_schema(n, "gb_zero")
            structure_schema = cgamma.load_structure_schema(n)
            self.assertEqual(schema["evaluated_structure_constants"], structure_schema["structure_constants"])
            self.assertEqual(schema["evaluation_profile"]["name"], "gb_zero")
            self.assertEqual(schema["consistency_with_schema_2"]["evaluated_gamma_nonzero_count"], 0)
            self.assertTrue(schema["consistency_with_schema_2"]["profile_matches_gamma_matrix"])
            self.assertTrue(schema["consistency_with_schema_2"]["gb_zero_recovers_schema_1"])

    def test_schema3_core_keys_for_n_1_2_3(self) -> None:
        expected_keys = {
            "schema_version",
            "algebra",
            "basis",
            "parity",
            "central_elements",
            "evaluation_profile",
            "evaluated_structure_constants",
            "consistency_with_schema_2",
            "metadata",
        }
        for n in (1, 2, 3):
            schema = cevaluated.build_evaluated_schema(n, "gb_zero")
            self.assertEqual(set(schema.keys()), expected_keys)
            self.assertEqual(schema["schema_version"], "5.0")
            self.assertEqual(schema["metadata"]["profile_name"], "gb_zero")


if __name__ == "__main__":
    unittest.main()
