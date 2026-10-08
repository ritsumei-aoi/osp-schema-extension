import json
import unittest
from fractions import Fraction
from pathlib import Path

from src.C_gamma import (
    _add,
    _as_deformed,
    _deformed_normalizer,
    _multiply,
    build_gamma_schema,
)
from src.C_generators import build_generators, graded_bracket


class CGammaTests(unittest.TestCase):
    def test_oscillator_rewrite_rules(self):
        normalize = _deformed_normalizer(1)
        mixed = normalize(("b_1_p", "a_1_p"))
        self.assertEqual(
            set(mixed),
            {
                (("a_1_p", "b_1_p"), None, Fraction(1)),
                ((), "gb_a1_p_b1_p", Fraction(-1)),
            },
        )
        fermion = normalize(("a_1_m", "a_1_p"))
        self.assertEqual(
            set(fermion),
            {
                ((), None, Fraction(1)),
                (("a_1_p", "a_1_m"), None, Fraction(-1)),
            },
        )
        boson = normalize(("b_1_m", "b_1_p"))
        self.assertEqual(
            set(boson),
            {
                ((), None, Fraction(1)),
                (("b_1_p", "b_1_m"), None, Fraction(1)),
            },
        )

    def test_gamma_files_are_consistent_with_schema1(self):
        data_dir = Path(__file__).resolve().parents[1] / "data"
        for n in (1, 2, 3):
            with self.subTest(n=n):
                gamma = build_gamma_schema(n, "2026-10-08")
                stored_gamma = json.loads((data_dir / f"C_{n}_gamma.json").read_text())
                self.assertEqual(
                    stored_gamma["gb_matrix"],
                    gamma["gb_matrix"],
                )
                self.assertEqual(
                    stored_gamma["inhomogeneous_deformation"],
                    gamma["inhomogeneous_deformation"],
                )
                structure = json.loads((data_dir / f"C_{n}_structure.json").read_text())
                gb = gamma["gb_matrix"]
                self.assertEqual(gb["shape"], [2, 2 * n])
                self.assertEqual(len(gb["entries"]), 2)
                self.assertTrue(all(len(row) == 2 * n for row in gb["entries"]))
                parameters = {parameter for row in gb["entries"] for parameter in row}
                self.assertEqual(len(parameters), 4 * n)
                basis = set(structure["basis"]["even"] + structure["basis"]["odd"])
                seen = set()
                for row in gamma["inhomogeneous_deformation"]["gamma_coefficients"]:
                    self.assertIn(row["X"], basis)
                    self.assertIn(row["Y"], basis)
                    self.assertIn(row["Z"], basis | {"K"})
                    key = (row["X"], row["Y"], row["Z"])
                    self.assertNotIn(key, seen)
                    seen.add(key)
                    term_names = [term["parameter"] for term in row["terms"]]
                    self.assertEqual(len(term_names), len(set(term_names)))
                    self.assertTrue(set(term_names) <= parameters)
                    self.assertTrue(all(Fraction(term["coeff"]) for term in row["terms"]))

    def test_undeformed_parts_match_schema1_brackets(self):
        for n in (1, 2, 3):
            with self.subTest(n=n):
                generators = build_generators(n)
                normalize = _deformed_normalizer(n)
                for index, left in enumerate(generators):
                    for right in generators[index:]:
                        forward = _multiply(
                            _as_deformed(left), _as_deformed(right), n, normalize
                        )
                        reverse = _multiply(
                            _as_deformed(right), _as_deformed(left), n, normalize
                        )
                        sign = -1 if left.parity and right.parity else 1
                        _add(forward, reverse, -sign)
                        actual = {
                            monomial: coeff
                            for (monomial, parameter), coeff in forward.items()
                            if parameter is None and coeff
                        }
                        expected = graded_bracket(
                            left.realization,
                            right.realization,
                            left.parity,
                            right.parity,
                            n,
                        )
                        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
