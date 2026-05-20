from __future__ import annotations

import sys
import unittest
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import C_gamma as cgamma


class CGammaTestCase(unittest.TestCase):
    def test_gb_matrix_layout_for_n_1_2_3(self) -> None:
        for n in (1, 2, 3):
            deformation = cgamma.build_inhomogeneous_deformation(n)
            gb_matrix = deformation["gb_matrix"]
            self.assertEqual(gb_matrix["rows"], ["a_1_p", "a_1_m"])
            self.assertEqual(gb_matrix["columns"], cgamma.gb_columns(n))
            self.assertEqual(len(gb_matrix["entries"]), 2)
            self.assertEqual(len(gb_matrix["entries"][0]), 2 * n)
            self.assertEqual(len(gb_matrix["entries"][1]), 2 * n)

    def test_known_n1_odd_odd_gamma(self) -> None:
        gamma = cgamma.gamma_in_basis(1, "E_eps1_del1_pp", "E_eps1_del1_mp")
        self.assertEqual(
            gamma,
            {
                "E_eps1_del1_pp": {"gb_a1m_b1p": Fraction(-1)},
                "E_eps1_del1_mp": {"gb_a1p_b1p": Fraction(-1)},
            },
        )

    def test_even_even_gamma_is_zero_for_n_1_2_3(self) -> None:
        for n in (1, 2, 3):
            schema = cgamma.load_structure_schema(n)
            purely_bosonic_even = [name for name in schema["basis"]["even"] if name != "H_1"]
            for left in purely_bosonic_even:
                for right in purely_bosonic_even:
                    self.assertEqual(cgamma.gamma_in_basis(n, left, right), {})

    def test_gamma_decomposition_can_use_K_for_n1(self) -> None:
        decomposition = cgamma.decompose_gamma_expression_to_basis(
            1,
            {("a_1_p", "a_1_m"): Fraction(-1)},
        )
        self.assertEqual(
            decomposition,
            {"H_1": Fraction(-1), "H_2": Fraction(-1), "K": Fraction(-1, 2)},
        )

    def test_schema2_consistency_with_schema1_for_n_1_2_3(self) -> None:
        for n in (1, 2, 3):
            schema = cgamma.build_gamma_schema(n)
            report = schema["consistency_with_schema_1"]
            self.assertTrue(report["algebra_match"])
            self.assertTrue(report["basis_match"])
            self.assertTrue(report["parity_match"])
            self.assertTrue(report["central_elements_match"])
            self.assertGreater(len(schema["inhomogeneous_deformation"]["gamma_matrix"]), 0)


if __name__ == "__main__":
    unittest.main()
