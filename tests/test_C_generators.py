#!/usr/bin/env python3
"""
Unit tests for C(n+1) generator

Tests parity, generator counts, schema consistency, and dimension formulas.
"""

import unittest
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from C_generators import CnGenerator


class TestCnGeneratorDimensions(unittest.TestCase):
    """Test dimension formulas for C(n+1)."""

    def test_c2_dimensions(self):
        """C(2) = osp(2|2) should have dim(even)=4, dim(odd)=4."""
        gen = CnGenerator(1)
        self.assertEqual(gen.even_dim, 4)
        self.assertEqual(gen.odd_dim, 4)
        self.assertEqual(gen.total_dim, 8)

    def test_c3_dimensions(self):
        """C(3) = osp(2|4) should have dim(even)=11, dim(odd)=8."""
        gen = CnGenerator(2)
        self.assertEqual(gen.even_dim, 11)
        self.assertEqual(gen.odd_dim, 8)
        self.assertEqual(gen.total_dim, 19)

    def test_c4_dimensions(self):
        """C(4) = osp(2|6) should have dim(even)=22, dim(odd)=12."""
        gen = CnGenerator(3)
        self.assertEqual(gen.even_dim, 22)
        self.assertEqual(gen.odd_dim, 12)
        self.assertEqual(gen.total_dim, 34)

    def test_dimension_formula(self):
        """Test dimension formula: even = 2n^2 + n + 1, odd = 4n."""
        for n in range(1, 5):
            gen = CnGenerator(n)
            expected_even = 2 * n**2 + n + 1
            expected_odd = 4 * n
            self.assertEqual(gen.even_dim, expected_even,
                           f"C({n+1}): even dimension formula failed")
            self.assertEqual(gen.odd_dim, expected_odd,
                           f"C({n+1}): odd dimension formula failed")


class TestCnGeneratorBasis(unittest.TestCase):
    """Test basis construction for C(n+1)."""

    def test_cartan_count(self):
        """Cartan subalgebra should have n+1 elements for C(n+1)."""
        for n in range(1, 4):
            gen = CnGenerator(n)
            self.assertEqual(len(gen.cartan), n + 1)

    def test_cartan_labels(self):
        """Cartan elements should be labeled H_1, ..., H_{n+1}."""
        gen = CnGenerator(2)
        expected = ["H_1", "H_2", "H_3"]
        self.assertEqual(gen.cartan, expected)

    def test_odd_roots_count(self):
        """Positive odd roots: 2n generators (ε+δ_k, ε-δ_k for k=1,...,n)."""
        for n in range(1, 4):
            gen = CnGenerator(n)
            self.assertEqual(len(gen.pos_odd), 2 * n)

    def test_positive_even_roots_count(self):
        """Count positive even roots."""
        # C(2): 2δ_1 (1 root) = 1
        gen = CnGenerator(1)
        self.assertEqual(len(gen.pos_even), 1)

        # C(3): 2δ_1, 2δ_2 (2) + δ_1-δ_2 (1) + δ_1+δ_2 (1) = 4
        gen = CnGenerator(2)
        self.assertEqual(len(gen.pos_even), 4)

        # C(4): 2δ_i (3) + (δ_i-δ_j, δ_i+δ_j) for i<j (6) = 9
        gen = CnGenerator(3)
        self.assertEqual(len(gen.pos_even), 9)

    def test_basis_size(self):
        """Total basis size should match dimension."""
        for n in range(1, 4):
            gen = CnGenerator(n)
            total_dim = gen.even_dim + gen.odd_dim
            self.assertEqual(len(gen.basis), total_dim,
                           f"C({n+1}): basis size mismatch")

    def test_no_duplicate_basis_elements(self):
        """All basis elements should be unique."""
        for n in range(1, 4):
            gen = CnGenerator(n)
            self.assertEqual(len(gen.basis), len(set(gen.basis)),
                           f"C({n+1}): duplicate basis elements")


class TestCnGeneratorParity(unittest.TestCase):
    """Test parity of generators."""

    def test_cartan_even_parity(self):
        """All Cartan elements should have parity 0 (even)."""
        for n in range(1, 4):
            gen = CnGenerator(n)
            schema = gen.generate_schema()
            for h in gen.cartan:
                self.assertEqual(schema["parity"][h], 0, f"{h} should be even")

    def test_odd_root_parity(self):
        """All E_eps generators should have parity 1 (odd)."""
        for n in range(1, 4):
            gen = CnGenerator(n)
            schema = gen.generate_schema()
            for g in gen.pos_odd:
                self.assertEqual(schema["parity"][g], 1,
                               f"{g} should be odd")
                neg_g = gen._negate_gen(g)
                self.assertEqual(schema["parity"][neg_g], 1,
                               f"{neg_g} should be odd")

    def test_even_root_parity(self):
        """All E_2del and E_del generators should have parity 0 (even)."""
        for n in range(1, 4):
            gen = CnGenerator(n)
            schema = gen.generate_schema()
            for g in gen.pos_even + gen.neg_even:
                self.assertEqual(schema["parity"][g], 0,
                               f"{g} should be even")


class TestCnGeneratorSchema(unittest.TestCase):
    """Test generated schema structure."""

    def test_schema_version(self):
        """Schema version should be 5.0."""
        for n in range(1, 4):
            gen = CnGenerator(n)
            schema = gen.generate_schema()
            self.assertEqual(schema["schema_version"], "5.0")

    def test_algebra_family(self):
        """Algebra family should be 'C'."""
        for n in range(1, 4):
            gen = CnGenerator(n)
            schema = gen.generate_schema()
            self.assertEqual(schema["algebra"]["family"], "C")

    def test_algebra_m(self):
        """m parameter should always be 1 for C(n+1)."""
        for n in range(1, 4):
            gen = CnGenerator(n)
            schema = gen.generate_schema()
            self.assertEqual(schema["algebra"]["m"], 1)

    def test_algebra_n(self):
        """n parameter should match bosonic rank."""
        for n in range(1, 4):
            gen = CnGenerator(n)
            schema = gen.generate_schema()
            self.assertEqual(schema["algebra"]["n"], n)

    def test_central_elements_present(self):
        """Central elements key should exist with κ and K."""
        for n in range(1, 4):
            gen = CnGenerator(n)
            schema = gen.generate_schema()
            self.assertIn("central_elements", schema)
            self.assertIn("kappa", schema["central_elements"])
            self.assertIn("K", schema["central_elements"])

    def test_oscillator_generators_fermions(self):
        """Fermions key should exist with a_1_p, a_1_m."""
        for n in range(1, 4):
            gen = CnGenerator(n)
            schema = gen.generate_schema()
            ferms = schema["oscillator_generators"]["fermions"]
            self.assertEqual(ferms["label"], "a_1")
            self.assertEqual(ferms["m"], 1)
            self.assertEqual(ferms["labels"], ["a_1_p", "a_1_m"])

    def test_basis_even_odd_count(self):
        """Basis even/odd counts should match dimensions."""
        for n in range(1, 4):
            gen = CnGenerator(n)
            schema = gen.generate_schema()
            basis = schema["basis"]
            self.assertEqual(len(basis["even"]), gen.even_dim)
            self.assertEqual(len(basis["odd"]), gen.odd_dim)

    def test_parity_dict_complete(self):
        """Parity dict should have all basis elements."""
        for n in range(1, 4):
            gen = CnGenerator(n)
            schema = gen.generate_schema()
            parity = schema["parity"]
            for g in gen.basis:
                self.assertIn(g, parity, f"Parity missing for {g}")

    def test_realizations_exist(self):
        """Generator realizations should exist for all basis elements."""
        for n in range(1, 4):
            gen = CnGenerator(n)
            schema = gen.generate_schema()
            realizations = schema["generator_realization"]["realizations"]
            # Should have realizations for basis elements
            self.assertGreater(len(realizations), 0)


class TestNegationLogic(unittest.TestCase):
    """Test the negation logic for generators."""

    def test_even_root_negation(self):
        """Test negation of even roots."""
        gen = CnGenerator(2)
        self.assertEqual(gen._negate_gen("E_2del1_p"), "E_2del1_m")
        self.assertEqual(gen._negate_gen("E_2del1_m"), "E_2del1_p")
        self.assertEqual(gen._negate_gen("E_del1_del2_pp"), "E_del1_del2_mm")
        self.assertEqual(gen._negate_gen("E_del1_del2_mm"), "E_del1_del2_pp")
        self.assertEqual(gen._negate_gen("E_del1_del2_pm"), "E_del1_del2_mp")
        self.assertEqual(gen._negate_gen("E_del1_del2_mp"), "E_del1_del2_pm")

    def test_odd_root_negation(self):
        """Test negation of odd roots."""
        gen = CnGenerator(1)
        self.assertEqual(gen._negate_gen("E_eps_del1_pp"), "E_eps_del1_mm")
        self.assertEqual(gen._negate_gen("E_eps_del1_mm"), "E_eps_del1_pp")
        self.assertEqual(gen._negate_gen("E_eps_del1_pm"), "E_eps_del1_mp")
        self.assertEqual(gen._negate_gen("E_eps_del1_mp"), "E_eps_del1_pm")

    def test_double_negation(self):
        """Double negation should return original."""
        gen = CnGenerator(2)
        generators = ["E_2del1_p", "E_eps_del1_pp", "E_eps_del1_pm"]
        for g in generators:
            self.assertEqual(gen._negate_gen(gen._negate_gen(g)), g)


class TestJSONValidity(unittest.TestCase):
    """Test that generated JSON files are valid."""

    def test_json_files_valid(self):
        """All JSON files should be valid JSON."""
        for n in [1, 2, 3]:
            filepath = Path(__file__).parent.parent / f"data" / f"C_{n}_structure.json"
            if filepath.exists():
                with open(filepath) as f:
                    schema = json.load(f)
                    self.assertIsInstance(schema, dict)
                    self.assertIn("schema_version", schema)
                    self.assertIn("algebra", schema)


if __name__ == "__main__":
    unittest.main()
