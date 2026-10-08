import unittest
from fractions import Fraction
from itertools import product

from src.C_generators import build_generators, build_schema


class CGeneratorTests(unittest.TestCase):
    def test_basis_counts_and_parities(self):
        for n in (1, 2, 3):
            with self.subTest(n=n):
                schema = build_schema(n, "2026-10-08")
                even = schema["basis"]["even"]
                odd = schema["basis"]["odd"]
                self.assertEqual(len(even), 2 * n * n + n + 1)
                self.assertEqual(len(odd), 4 * n)
                self.assertEqual(set(even) | set(odd), set(schema["parity"]))
                self.assertEqual({schema["parity"][label] for label in even}, {0})
                self.assertEqual({schema["parity"][label] for label in odd}, {1})
                self.assertEqual(
                    len(schema["generator_realization"]["realizations"]),
                    len(even) + len(odd),
                )

    def test_structure_constants_are_well_formed_and_parity_consistent(self):
        for n in (1, 2, 3):
            with self.subTest(n=n):
                schema = build_schema(n, "2026-10-08")
                parity = schema["parity"]
                labels = set(parity)
                for bracket in schema["structure_constants"]:
                    self.assertEqual(bracket["sign_rule"], "graded")
                    self.assertTrue({bracket["X"], bracket["Y"], bracket["Z"]} <= labels)
                    self.assertEqual(
                        parity[bracket["Z"]],
                        parity[bracket["X"]] ^ parity[bracket["Y"]],
                    )
                    self.assertTrue(bracket["coeff"])
                    self.assertLessEqual(
                        schema["basis"]["even"].index(bracket["X"])
                        if bracket["X"] in schema["basis"]["even"]
                        else len(schema["basis"]["even"]) +
                             schema["basis"]["odd"].index(bracket["X"]),
                        schema["basis"]["even"].index(bracket["Y"])
                        if bracket["Y"] in schema["basis"]["even"]
                        else len(schema["basis"]["even"]) +
                             schema["basis"]["odd"].index(bracket["Y"]),
                    )

    def test_generator_realizations_have_expected_cardinalities(self):
        for n in (1, 2, 3):
            with self.subTest(n=n):
                generators = build_generators(n)
                self.assertEqual(len(generators), 2 * n * n + 5 * n + 1)
                self.assertEqual(len({generator.label for generator in generators}),
                                 len(generators))
                self.assertEqual(sum(generator.parity for generator in generators), 4 * n)

    def test_structure_constants_satisfy_super_jacobi(self):
        for n in (1, 2, 3):
            with self.subTest(n=n):
                schema = build_schema(n, "2026-10-08")
                labels = schema["basis"]["even"] + schema["basis"]["odd"]
                parity = schema["parity"]
                entries = {}
                for row in schema["structure_constants"]:
                    entries.setdefault((row["X"], row["Y"]), {})[row["Z"]] = Fraction(
                        row["coeff"]
                    )

                def bracket(left, right):
                    direct = entries.get((left, right))
                    if direct is not None:
                        return direct
                    sign = -1 if parity[left] and parity[right] else 1
                    return {
                        label: -sign * coeff
                        for label, coeff in entries.get((right, left), {}).items()
                    }

                for x, y, z in product(labels, repeat=3):
                    total = {}
                    terms = (
                        ((-1) ** (parity[x] * parity[z]), x, y, z),
                        ((-1) ** (parity[y] * parity[x]), y, z, x),
                        ((-1) ** (parity[z] * parity[y]), z, x, y),
                    )
                    for sign, outer_left, inner_left, inner_right in terms:
                        for middle, inner_coeff in bracket(inner_left, inner_right).items():
                            for result, outer_coeff in bracket(outer_left, middle).items():
                                total[result] = total.get(result, Fraction()) + (
                                    sign * inner_coeff * outer_coeff
                                )
                    self.assertFalse({label: coeff for label, coeff in total.items() if coeff})


if __name__ == "__main__":
    unittest.main()
