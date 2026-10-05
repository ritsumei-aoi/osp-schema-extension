"""
Unit tests for C(n+1) structure constant generator.

Author: Claude Haiku 4.5
"""

import unittest
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from C_generators import CNGenerator


class TestCGeneratorBasics(unittest.TestCase):
    """Test basic functionality of CNGenerator."""

    def test_dimension_C2(self):
        """Test C(2) = osp(2|2) dimensions."""
        gen = CNGenerator(1)
        self.assertEqual(len(gen.basis_labels), 8)
        eps_count = sum(1 for l in gen.basis_labels if l.startswith("E_eps"))
        H_count = sum(1 for l in gen.basis_labels if l.startswith("H_"))
        self.assertEqual(eps_count, 4)
        self.assertEqual(H_count, 2)

        schema = gen.to_json()
        self.assertEqual(schema["algebra"]["n"], 1)
        self.assertEqual(schema["algebra"]["dimension"]["total"], 8)
        self.assertEqual(schema["algebra"]["dimension"]["even"], 4)
        self.assertEqual(schema["algebra"]["dimension"]["odd"], 4)

    def test_dimension_C3(self):
        """Test C(3) = osp(2|4) dimensions."""
        gen = CNGenerator(2)
        total = 2*2*2 + 5*2 + 1
        even = 2*2*2 + 2 + 1
        odd = 4*2

        self.assertEqual(len(gen.basis_labels), total)
        schema = gen.to_json()
        self.assertEqual(schema["algebra"]["dimension"]["total"], total)
        self.assertEqual(schema["algebra"]["dimension"]["even"], even)
        self.assertEqual(schema["algebra"]["dimension"]["odd"], odd)

    def test_dimension_C4(self):
        """Test C(4) = osp(2|6) dimensions."""
        gen = CNGenerator(3)
        total = 2*3*3 + 5*3 + 1
        even = 2*3*3 + 3 + 1
        odd = 4*3

        self.assertEqual(len(gen.basis_labels), total)
        schema = gen.to_json()
        self.assertEqual(schema["algebra"]["dimension"]["total"], total)
        self.assertEqual(schema["algebra"]["dimension"]["even"], even)
        self.assertEqual(schema["algebra"]["dimension"]["odd"], odd)

    def test_parity_assignments(self):
        """Test that parity is correctly assigned."""
        gen = CNGenerator(2)
        schema = gen.to_json()

        for label in schema["basis"]["even"]:
            self.assertEqual(schema["parity"][label], 0, f"{label} should be even")

        for label in schema["basis"]["odd"]:
            self.assertEqual(schema["parity"][label], 1, f"{label} should be odd")

    def test_schema_structure(self):
        """Test that schema has all required top-level keys."""
        gen = CNGenerator(1)
        schema = gen.to_json()

        required_keys = [
            "schema_version",
            "algebra",
            "oscillator_generators",
            "oscillator_relations",
            "central_elements",
            "basis",
            "parity",
            "generator_realization",
            "structure_constants",
            "metadata"
        ]

        for key in required_keys:
            self.assertIn(key, schema, f"Missing key: {key}")

    def test_algebra_field(self):
        """Test algebra field has correct structure."""
        gen = CNGenerator(1)
        schema = gen.to_json()
        alg = schema["algebra"]

        self.assertEqual(alg["family"], "C")
        self.assertEqual(alg["m"], 1)
        self.assertEqual(alg["n"], 1)
        self.assertEqual(alg["dimension"]["total"], 8)

    def test_oscillator_generators(self):
        """Test oscillator generators field."""
        gen = CNGenerator(2)
        schema = gen.to_json()
        osc_gen = schema["oscillator_generators"]

        self.assertIn("fermions", osc_gen)
        self.assertIn("bosons", osc_gen)
        self.assertEqual(osc_gen["fermions"]["m"], 1)
        self.assertEqual(osc_gen["fermions"]["count"], 2)
        self.assertEqual(osc_gen["bosons"]["n"], 2)
        self.assertEqual(osc_gen["bosons"]["count"], 4)

    def test_central_elements(self):
        """Test central elements field."""
        gen = CNGenerator(1)
        schema = gen.to_json()

        self.assertIn("central_elements", schema)
        self.assertIn("kappa", schema["central_elements"])
        self.assertIn("K", schema["central_elements"])
        self.assertEqual(schema["central_elements"]["kappa"]["parity"], 1)
        self.assertEqual(schema["central_elements"]["K"]["parity"], 0)

    def test_basis_completeness(self):
        """Test that all basis labels appear in basis and parity."""
        gen = CNGenerator(2)
        schema = gen.to_json()

        basis_total = len(schema["basis"]["even"]) + len(schema["basis"]["odd"])
        parity_total = len(schema["parity"])

        self.assertEqual(basis_total, parity_total)
        self.assertEqual(basis_total, len(gen.basis_labels))

    def test_generator_realization_parity(self):
        """Test that generator realizations have correct parity."""
        gen = CNGenerator(1)
        schema = gen.to_json()

        for label, real in schema["generator_realization"].items():
            expected_parity = schema["parity"][label]
            self.assertEqual(real["parity"], expected_parity,
                           f"{label} realization parity mismatch")


class TestCGeneratorOscillators(unittest.TestCase):
    """Test oscillator realization correctness."""

    def test_fermionic_generator_form(self):
        """Test that fermionic generators have a_1_p or a_1_m."""
        gen = CNGenerator(1)
        schema = gen.to_json()

        for label in schema["basis"]["odd"]:
            real = schema["generator_realization"][label]
            words_list = [w for sf in real["standard_form"] for w in sf["words"]]
            self.assertTrue(
                any(w.startswith("a_1") for w in words_list),
                f"{label} missing fermionic oscillator"
            )

    def test_cartan_generator_form(self):
        """Test Cartan generators have expected form."""
        gen = CNGenerator(2)
        schema = gen.to_json()

        H_labels = [l for l in schema["basis"]["even"] if l.startswith("H_")]
        self.assertEqual(len(H_labels), 3)

        for label in H_labels:
            real = schema["generator_realization"][label]
            self.assertGreater(len(real["standard_form"]), 0)


class TestJSONValidity(unittest.TestCase):
    """Test generated JSON files are valid."""

    def test_json_files_valid(self):
        """Test that generated JSON files are valid JSON."""
        for n in [1, 2, 3]:
            filename = f"data/C_{n}_structure.json"
            self.assertTrue(os.path.exists(filename), f"Missing {filename}")

            with open(filename, "r") as f:
                data = json.load(f)

            self.assertEqual(data["algebra"]["n"], n)
            self.assertEqual(data["schema_version"], "5.0")
            self.assertEqual(data["algebra"]["family"], "C")
            self.assertEqual(data["algebra"]["m"], 1)

    def test_json_schema_consistency(self):
        """Test that JSON schema values are internally consistent."""
        gen = CNGenerator(2)
        schema = gen.to_json()

        basis_count = len(schema["basis"]["even"]) + len(schema["basis"]["odd"])
        expected_even = 2*2*2 + 2 + 1
        expected_odd = 4*2
        expected_total = expected_even + expected_odd

        self.assertEqual(len(schema["basis"]["even"]), expected_even)
        self.assertEqual(len(schema["basis"]["odd"]), expected_odd)
        self.assertEqual(basis_count, expected_total)


if __name__ == "__main__":
    unittest.main()
