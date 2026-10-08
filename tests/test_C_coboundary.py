import json
import unittest
from fractions import Fraction
from pathlib import Path

from src.C_coboundary import (
    _bracket_table,
    _coboundary_pair,
    build_coboundary_schema,
)


class CCoboundaryTests(unittest.TestCase):
    def test_odd_map_parameters_and_outputs_match_schema1(self):
        data_dir = Path(__file__).resolve().parents[1] / "data"
        for n in (1, 2, 3):
            with self.subTest(n=n):
                structure = json.loads(
                    (data_dir / f"C_{n}_structure.json").read_text()
                )
                coboundary = build_coboundary_schema(structure, "2026-10-08")
                stored = json.loads(
                    (data_dir / f"C_{n}_coboundary.json").read_text()
                )
                self.assertEqual(stored["odd_linear_map"], coboundary["odd_linear_map"])
                self.assertEqual(
                    stored["coboundary"]["coefficients"],
                    coboundary["coboundary"]["coefficients"],
                )
                labels = set(structure["basis"]["even"] + structure["basis"]["odd"])
                parameters = coboundary["odd_linear_map"]["parameters"]
                self.assertEqual(
                    len(parameters),
                    2 * len(structure["basis"]["even"]) * len(structure["basis"]["odd"]),
                )
                for parameter in parameters:
                    self.assertIn(parameter["source"], labels)
                    self.assertIn(parameter["target"], labels)
                    self.assertNotEqual(
                        structure["parity"][parameter["source"]],
                        structure["parity"][parameter["target"]],
                    )
                for row in coboundary["coboundary"]["coefficients"]:
                    self.assertTrue({row["X"], row["Y"], row["Z"]} <= labels)
                    for term in row["terms"]:
                        self.assertTrue(term["parameter"].startswith("phi_"))
                        self.assertNotEqual(Fraction(term["coeff"]), 0)

    def test_coboundary_output_parity_is_odd(self):
        data_dir = Path(__file__).resolve().parents[1] / "data"
        for n in (1, 2, 3):
            with self.subTest(n=n):
                schema = json.loads(
                    (data_dir / f"C_{n}_coboundary.json").read_text()
                )
                parity = schema["parity"]
                for row in schema["coboundary"]["coefficients"]:
                    self.assertEqual(
                        parity[row["Z"]],
                        parity[row["X"]] ^ parity[row["Y"]] ^ 1,
                    )

    def test_coboundary_is_graded_skew_symmetric(self):
        data_dir = Path(__file__).resolve().parents[1] / "data"
        for n in (1, 2, 3):
            with self.subTest(n=n):
                structure = json.loads(
                    (data_dir / f"C_{n}_structure.json").read_text()
                )
                labels, parity, entries = _bracket_table(structure)
                for x in labels:
                    for y in labels:
                        forward = _coboundary_pair(x, y, labels, parity, entries)
                        reverse = _coboundary_pair(y, x, labels, parity, entries)
                        scale = -(-1 if parity[x] and parity[y] else 1)
                        expected = {
                            z: {
                                parameter: scale * coeff
                                for parameter, coeff in terms.items()
                                if scale * coeff
                            }
                            for z, terms in forward.items()
                        }
                        expected = {
                            z: terms for z, terms in expected.items() if terms
                        }
                        self.assertEqual(reverse, expected)


if __name__ == "__main__":
    unittest.main()
