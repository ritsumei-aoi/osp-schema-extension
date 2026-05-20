from __future__ import annotations

import sys
import unittest
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import C_coboundary as ccob
import C_generators as cg


class CCoboundaryTestCase(unittest.TestCase):
    def test_gb_one_profile_covers_all_parameters_for_n_1_2_3(self) -> None:
        for n in (1, 2, 3):
            profile = ccob.build_profile_assignments(n, "gb_one")
            self.assertEqual(list(profile["gb_values"].keys()), ccob.cgamma.gb_labels_in_order(n))
            self.assertTrue(all(value == Fraction(1) for value in profile["gb_values"].values()))

    def test_basis_map_delta_is_graded_antisymmetric_for_n1(self) -> None:
        n = 1
        vector = ccob.build_basis_map_column(n, "H_1", "E_eps1_del1_pp")
        data = ccob.build_column_data(n)
        basis_names = data["basis_order"]
        target_names = data["target_order"]
        basis_count = len(basis_names)
        target_count = len(target_names)
        parity = data["parity"]

        def coefficient(left: str, right: str, result: str) -> Fraction:
            index = ccob.row_index(
                data["basis_index"][left],
                data["basis_index"][right],
                data["target_index"][result],
                basis_count,
                target_count,
            )
            return vector.get(index, Fraction(0))

        for left in basis_names:
            for right in basis_names:
                sign = Fraction(-1 if (parity[left] * parity[right]) % 2 else 1)
                for result in basis_names:
                    self.assertEqual(
                        coefficient(left, right, result),
                        -sign * coefficient(right, left, result),
                    )

    def test_gb_one_target_has_k_obstruction_for_n_1_2_3(self) -> None:
        for n in (1, 2, 3):
            verification = ccob.verify_rank_condition(n, "gb_one")
            self.assertGreater(verification["gamma_k_nonzero_count"], 0)
            self.assertFalse(verification["is_trivial"])

    def test_nontrivial_conclusion_for_n_1_2_3(self) -> None:
        for n in (1, 2, 3):
            schema = ccob.build_coboundary_schema(n, "gb_one")
            self.assertEqual(schema["conclusion"]["classification"], "Non-trivial")
            self.assertGreater(schema["rank_verification"]["augmented_rank"], schema["rank_verification"]["operator_rank"])


if __name__ == "__main__":
    unittest.main()
