import json
import sys
import unittest
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from C_coboundary import (  # noqa: E402
    build_coboundary_schema,
    verify_coboundary_schema,
)
from C_gamma import _load_structure  # noqa: E402
from C_generators import build_basis  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
GENERATION_DATE = "2026-10-10"


class CCoboundaryTests(unittest.TestCase):
    def _load_structure(self, rank):
        basis = build_basis(rank)
        path = ROOT / "data" / f"C_{rank}_structure.json"
        return basis, _load_structure(path, basis)

    def test_general_odd_map_parameterization_and_layer1_consistency(self):
        for rank in (1, 2, 3):
            with self.subTest(rank=rank):
                basis, structure = self._load_structure(rank)
                schema, checked_pairs, term_count = build_coboundary_schema(
                    basis, structure, generation_date=GENERATION_DATE
                )
                map_data = schema["odd_linear_map"]
                self.assertEqual(map_data["parity"], 1)
                self.assertEqual(map_data["global_scale"], "1")
                self.assertEqual(
                    map_data["parameter_count"],
                    2 * len(basis.even) * len(basis.odd),
                )
                self.assertEqual(
                    checked_pairs,
                    len(basis.pbw) ** 2,
                )
                self.assertGreater(term_count, 0)
                self.assertEqual(schema["schema_layer"], 4)
                self.assertEqual(schema["schema_type"], "coboundary_structure")
                self.assertEqual(
                    schema["metadata"]["source_schema"],
                    f"C_{rank}_structure.json",
                )
                self.assertTrue(
                    all(
                        entry["source"] in basis.parity
                        and entry["target"] in basis.parity
                        and basis.parity[entry["target"]]
                        == (basis.parity[entry["source"]] + 1) % 2
                        for entry in map_data["coefficients"]
                    )
                )
                self.assertEqual(
                    verify_coboundary_schema(basis, structure, schema),
                    (checked_pairs, term_count),
                )

    def test_rank_one_coefficient_matches_the_coboundary_formula(self):
        basis, structure = self._load_structure(1)
        schema, _, _ = build_coboundary_schema(
            basis, structure, generation_date=GENERATION_DATE
        )
        key = (
            "H_1",
            "E_eps1_del1_pp",
            "H_1",
            "phi__E_eps1_del1_mm__from__H_1",
        )
        coefficients = {
            (record["X"], record["Y"], record["Z"], term["parameter"]): Fraction(
                term["scalar"]
            )
            for record in schema["coboundary_constants"]
            for term in record["coeff"]
        }
        self.assertEqual(coefficients[key], Fraction(-1))

    def test_verifier_rejects_modified_coefficient_and_missing_orientation(self):
        basis, structure = self._load_structure(1)
        schema, _, _ = build_coboundary_schema(
            basis, structure, generation_date=GENERATION_DATE
        )
        broken = json.loads(json.dumps(schema))
        broken["coboundary_constants"][0]["coeff"][0]["scalar"] = "999"
        with self.assertRaisesRegex(ValueError, "does not match the Layer 1"):
            verify_coboundary_schema(basis, structure, broken)

        broken = json.loads(json.dumps(schema))
        broken["coboundary_constants"].pop()
        with self.assertRaisesRegex(ValueError, "does not match the Layer 1"):
            verify_coboundary_schema(basis, structure, broken)


if __name__ == "__main__":
    unittest.main()
