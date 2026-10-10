import itertools
import json
import sys
import unittest
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from C_generators import (  # noqa: E402
    _add,
    _bracket,
    _express_in_basis,
    _scale,
    build_basis,
    build_schema,
    generate_structure_constants,
)


def _parse_coefficient(value):
    return Fraction(value)


class CGeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bases = {rank: build_basis(rank) for rank in (1, 2, 3)}
        cls.constants = {
            rank: generate_structure_constants(basis)
            for rank, basis in cls.bases.items()
        }

    def _structure_map(self, basis, records):
        result = {}
        for record in records:
            key = (record["X"], record["Y"])
            result.setdefault(key, {})[record["Z"]] = _parse_coefficient(
                record["coeff"]
            )
        return result

    def _bracket_coordinates(self, structure, left, right):
        return structure.get((left, right), {})

    def _nested_bracket(self, structure, left, inner):
        result = {}
        for inner_label, coefficient in inner.items():
            bracket = self._bracket_coordinates(structure, left, inner_label)
            result = _add(result, _scale(bracket, coefficient))
        return result

    def test_basis_cardinality_parity_and_powers(self):
        for rank, basis in self.bases.items():
            with self.subTest(rank=rank):
                self.assertEqual(len(basis.even), 2 * rank**2 + rank + 1)
                self.assertEqual(len(basis.odd), 4 * rank)
                self.assertEqual(len(set(basis.even)), len(basis.even))
                self.assertEqual(len(set(basis.odd)), len(basis.odd))
                self.assertEqual(set(basis.parity), set(basis.even) | set(basis.odd))
                self.assertTrue(all(basis.parity[label] == 0 for label in basis.even))
                self.assertTrue(all(basis.parity[label] == 1 for label in basis.odd))
                self.assertEqual(set(basis.pbw), set(basis.parity))

    def test_all_pairs_close_and_obey_graded_skew_symmetry(self):
        for rank, basis in self.bases.items():
            with self.subTest(rank=rank):
                for left, right in itertools.product(basis.pbw, repeat=2):
                    forward = _bracket(
                        basis.realizations[left],
                        basis.realizations[right],
                        basis.parity[left],
                        basis.parity[right],
                    )
                    reverse = _bracket(
                        basis.realizations[right],
                        basis.realizations[left],
                        basis.parity[right],
                        basis.parity[left],
                    )
                    factor = -1 if basis.parity[left] * basis.parity[right] == 0 else 1
                    self.assertEqual(forward, _scale(reverse, Fraction(factor)))

    def test_generated_constants_include_every_ordered_bracket(self):
        for rank, basis in self.bases.items():
            structure = self._structure_map(basis, self.constants[rank])
            with self.subTest(rank=rank):
                for left, right in itertools.product(basis.pbw, repeat=2):
                    oscillator_bracket = _bracket(
                        basis.realizations[left],
                        basis.realizations[right],
                        basis.parity[left],
                        basis.parity[right],
                    )
                    expected = _express_in_basis(oscillator_bracket, basis)
                    self.assertEqual(
                        structure.get((left, right), {}),
                        expected,
                        (rank, left, right),
                    )

    def test_super_jacobi_identity(self):
        for rank, basis in self.bases.items():
            structure = self._structure_map(basis, self.constants[rank])
            with self.subTest(rank=rank):
                for x, y, z in itertools.product(basis.pbw, repeat=3):
                    yz = self._bracket_coordinates(
                        structure, y, z
                    )
                    zx = self._bracket_coordinates(
                        structure, z, x
                    )
                    xy = self._bracket_coordinates(
                        structure, x, y
                    )
                    first = self._nested_bracket(structure, x, yz)
                    second = self._nested_bracket(structure, y, zx)
                    third = self._nested_bracket(structure, z, xy)

                    first_sign = -1 if basis.parity[x] * basis.parity[z] else 1
                    second_sign = -1 if basis.parity[y] * basis.parity[x] else 1
                    third_sign = -1 if basis.parity[z] * basis.parity[y] else 1
                    jacobi = _add(
                        _add(
                            _scale(first, Fraction(first_sign)),
                            _scale(second, Fraction(second_sign)),
                        ),
                        _scale(third, Fraction(third_sign)),
                    )
                    self.assertEqual(jacobi, {}, (rank, x, y, z, jacobi))

    def test_schema_payload_matches_specification(self):
        required_top_level = {
            "schema_version",
            "algebra",
            "oscillator_generators",
            "oscillator_relations",
            "central_elements",
            "basis",
            "parity",
            "generator_realization",
            "structure_constants",
            "metadata",
        }
        for rank, basis in self.bases.items():
            with self.subTest(rank=rank):
                schema = build_schema(
                    basis,
                    self.constants[rank],
                    generation_date="2026-10-10",
                )
                self.assertEqual(set(schema), required_top_level)
                self.assertEqual(schema["schema_version"], "5.0")
                self.assertEqual(schema["algebra"]["family"], "C")
                self.assertEqual(schema["algebra"]["m"], 1)
                self.assertEqual(schema["algebra"]["n"], rank)
                self.assertEqual(
                    schema["algebra"]["dimension"]["even"],
                    2 * rank**2 + rank + 1,
                )
                self.assertEqual(schema["algebra"]["dimension"]["odd"], 4 * rank)
                self.assertEqual(
                    set(schema["generator_realization"]["realizations"]),
                    set(basis.even) | set(basis.odd),
                )
                self.assertEqual(set(schema["parity"]), set(basis.even) | set(basis.odd))
                self.assertEqual(
                    schema["oscillator_generators"]["bosons"]["count"], 2 * rank
                )
                self.assertEqual(
                    schema["oscillator_generators"]["fermions"]["labels"],
                    ["a_1_p", "a_1_m"],
                )
                self.assertTrue(
                    all(
                        record["sign_rule"] == "graded"
                        and Fraction(record["coeff"]) != 0
                        for record in schema["structure_constants"]
                    )
                )
                json.dumps(schema, ensure_ascii=False)


if __name__ == "__main__":
    unittest.main()
