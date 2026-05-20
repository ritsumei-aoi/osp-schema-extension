from __future__ import annotations

import sys
import unittest
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import C_generators as cg


def add_scaled_map(target: dict[str, Fraction], source: dict[str, Fraction], scale: Fraction) -> None:
    for name, coeff in source.items():
        new_coeff = target.get(name, Fraction(0)) + coeff * scale
        if new_coeff:
            target[name] = new_coeff
        elif name in target:
            del target[name]


def bracket_linear(n: int, left: dict[str, Fraction], right: dict[str, Fraction]) -> dict[str, Fraction]:
    result: dict[str, Fraction] = {}
    for left_name, left_coeff in left.items():
        for right_name, right_coeff in right.items():
            add_scaled_map(result, cg.bracket_in_basis(n, left_name, right_name), left_coeff * right_coeff)
    return result


class CGeneratorsTestCase(unittest.TestCase):
    def assertCoeffMapEqual(self, actual: dict[str, Fraction], expected: dict[str, Fraction]) -> None:
        self.assertEqual(actual, expected)

    def test_basis_counts_for_n_1_2_3(self) -> None:
        expected = {
            1: (4, 4, 8),
            2: (11, 8, 19),
            3: (22, 12, 34),
        }
        for n, (even_count, odd_count, total_count) in expected.items():
            basis = cg.build_basis(n)
            self.assertEqual(len(basis["even"]), even_count)
            self.assertEqual(len(basis["odd"]), odd_count)
            self.assertEqual(len(basis["even"]) + len(basis["odd"]), total_count)

    def test_parity_counts_for_n_1_2_3(self) -> None:
        expected = {
            1: (4, 4),
            2: (11, 8),
            3: (22, 12),
        }
        for n, (even_count, odd_count) in expected.items():
            parity = cg.build_parity_map(n)
            self.assertEqual(sum(value == 0 for value in parity.values()), even_count)
            self.assertEqual(sum(value == 1 for value in parity.values()), odd_count)
            for name, value in parity.items():
                if name.startswith("E_eps1_del"):
                    self.assertEqual(value, 1)
                else:
                    self.assertEqual(value, 0)

    def test_n1_known_brackets(self) -> None:
        self.assertCoeffMapEqual(
            cg.bracket_in_basis(1, "H_1", "E_eps1_del1_pp"),
            {"E_eps1_del1_pp": Fraction(2)},
        )
        self.assertCoeffMapEqual(
            cg.bracket_in_basis(1, "H_1", "E_eps1_del1_pm"),
            {},
        )
        self.assertCoeffMapEqual(
            cg.bracket_in_basis(1, "E_eps1_del1_pp", "E_eps1_del1_mm"),
            {"H_1": Fraction(-1), "H_2": Fraction(-2)},
        )
        self.assertCoeffMapEqual(
            cg.bracket_in_basis(1, "E_2del1_p", "E_2del1_m"),
            {"H_2": Fraction(4)},
        )

    def test_schema_keys_and_core_fields_for_n_1_2_3(self) -> None:
        for n in (1, 2, 3):
            schema = cg.build_structure_schema(n)
            self.assertEqual(tuple(schema.keys()), cg.SCHEMA_TOP_LEVEL_KEYS)
            self.assertEqual(schema["schema_version"], "5.0")
            self.assertEqual(schema["algebra"]["family"], "C")
            self.assertEqual(schema["algebra"]["m"], 1)
            self.assertEqual(schema["oscillator_generators"]["standard_fermion"]["labels"], ["a_1_p", "a_1_m"])
            self.assertIn("kappa", schema["central_elements"])
            self.assertIn("K", schema["central_elements"])
            self.assertEqual(schema["basis"]["ordering_convention"], cg.ORDERING_CONVENTION)
            self.assertGreater(len(schema["structure_constants"]), 0)

    def test_graded_antisymmetry_for_all_n(self) -> None:
        for n in (1, 2, 3):
            parity = cg.build_parity_map(n)
            basis_order = cg.build_basis_order(n)
            for left_name in basis_order:
                for right_name in basis_order:
                    left = cg.bracket_in_basis(n, left_name, right_name)
                    right = cg.bracket_in_basis(n, right_name, left_name)
                    expected: dict[str, Fraction] = {}
                    sign = Fraction(-1 if (parity[left_name] * parity[right_name]) % 2 else 1)
                    for name, coeff in right.items():
                        expected[name] = -sign * coeff
                    self.assertCoeffMapEqual(left, expected)

    def test_jacobi_spot_check_n1(self) -> None:
        parity = cg.build_parity_map(1)
        x = {"E_eps1_del1_pp": Fraction(1)}
        y = {"E_eps1_del1_mm": Fraction(1)}
        z = {"H_2": Fraction(1)}

        first = bracket_linear(1, x, bracket_linear(1, y, z))
        second = bracket_linear(1, y, bracket_linear(1, z, x))
        third = bracket_linear(1, z, bracket_linear(1, x, y))

        jacobi: dict[str, Fraction] = {}
        add_scaled_map(jacobi, first, Fraction((-1) ** (parity["E_eps1_del1_pp"] * parity["H_2"])))
        add_scaled_map(jacobi, second, Fraction((-1) ** (parity["E_eps1_del1_mm"] * parity["E_eps1_del1_pp"])))
        add_scaled_map(jacobi, third, Fraction((-1) ** (parity["H_2"] * parity["E_eps1_del1_mm"])))

        self.assertCoeffMapEqual(jacobi, {})


if __name__ == "__main__":
    unittest.main()
