#!/usr/bin/env python3
"""
Unit tests for C(n+1) structure constant generator.
"""

import unittest
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from C_generators import CnGenerator


class TestCnGeneratorBasis(unittest.TestCase):
    """Test basis generation for C(n+1)."""

    def test_c2_basis_count(self):
        """C(2) should have 4 even + 4 odd generators."""
        gen = CnGenerator(1)
        self.assertEqual(len(gen.basis_even), 4)
        self.assertEqual(len(gen.basis_odd), 4)

    def test_c3_basis_count(self):
        """C(3) should have 11 even + 8 odd generators."""
        gen = CnGenerator(2)
        self.assertEqual(len(gen.basis_even), 11)
        self.assertEqual(len(gen.basis_odd), 8)

    def test_c4_basis_count(self):
        """C(4) should have 22 even + 12 odd generators."""
        gen = CnGenerator(3)
        self.assertEqual(len(gen.basis_even), 22)
        self.assertEqual(len(gen.basis_odd), 12)

    def test_c2_basis_structure(self):
        """C(2) basis should contain expected generators."""
        gen = CnGenerator(1)
        expected_even = ['H_1', 'H_2', 'E_2del1_p', 'E_2del1_m']
        self.assertEqual(gen.basis_even, expected_even)

        expected_odd = [
            'E_eps_del1_pp', 'E_eps_del1_pm',
            'E_eps_del1_mp', 'E_eps_del1_mm'
        ]
        self.assertEqual(gen.basis_odd, expected_odd)


class TestCnGeneratorParity(unittest.TestCase):
    """Test parity assignment."""

    def test_c2_parity(self):
        """C(2) generators should have correct parity."""
        gen = CnGenerator(1)

        # Even generators
        for gen_name in gen.basis_even:
            self.assertEqual(gen.parity[gen_name], 0, f"{gen_name} should be even")

        # Odd generators
        for gen_name in gen.basis_odd:
            self.assertEqual(gen.parity[gen_name], 1, f"{gen_name} should be odd")

    def test_c3_parity(self):
        """C(3) generators should have correct parity."""
        gen = CnGenerator(2)

        for gen_name in gen.basis_even:
            self.assertEqual(gen.parity[gen_name], 0)

        for gen_name in gen.basis_odd:
            self.assertEqual(gen.parity[gen_name], 1)


class TestCnGeneratorDimensions(unittest.TestCase):
    """Test dimension calculations."""

    def test_c2_dimensions(self):
        """C(2) should have dimensions (4, 4, 8)."""
        gen = CnGenerator(1)
        even, odd, total = gen._get_dimension()
        self.assertEqual(even, 4)
        self.assertEqual(odd, 4)
        self.assertEqual(total, 8)

    def test_c3_dimensions(self):
        """C(3) should have dimensions (11, 8, 19)."""
        gen = CnGenerator(2)
        even, odd, total = gen._get_dimension()
        self.assertEqual(even, 11)
        self.assertEqual(odd, 8)
        self.assertEqual(total, 19)

    def test_c4_dimensions(self):
        """C(4) should have dimensions (22, 12, 34)."""
        gen = CnGenerator(3)
        even, odd, total = gen._get_dimension()
        self.assertEqual(even, 22)
        self.assertEqual(odd, 12)
        self.assertEqual(total, 34)

    def test_dimension_formula(self):
        """Check dimension formula: even = 2n² + n + 1, odd = 4n."""
        for n in [1, 2, 3, 4]:
            gen = CnGenerator(n)
            even, odd, total = gen._get_dimension()
            expected_even = 2 * n * n + n + 1
            expected_odd = 4 * n
            expected_total = expected_even + expected_odd
            self.assertEqual(even, expected_even, f"even for n={n}")
            self.assertEqual(odd, expected_odd, f"odd for n={n}")
            self.assertEqual(total, expected_total, f"total for n={n}")


class TestCnGeneratorJSON(unittest.TestCase):
    """Test JSON schema generation."""

    def test_c2_json_structure(self):
        """C(2) JSON should have all required keys."""
        gen = CnGenerator(1)
        schema = gen.to_json()

        required_keys = [
            'schema_version', 'algebra', 'oscillator_generators',
            'oscillator_relations', 'central_elements', 'basis',
            'parity', 'generator_realization', 'structure_constants',
            'metadata'
        ]
        for key in required_keys:
            self.assertIn(key, schema, f"Missing key: {key}")

    def test_c2_algebra_field(self):
        """C(2) algebra field should have correct values."""
        gen = CnGenerator(1)
        schema = gen.to_json()
        alg = schema['algebra']

        self.assertEqual(alg['family'], 'C')
        self.assertEqual(alg['m'], 1)
        self.assertEqual(alg['n'], 1)
        self.assertEqual(alg['cartan_type'], 'C(2)')
        self.assertEqual(alg['dimension']['even'], 4)
        self.assertEqual(alg['dimension']['odd'], 4)
        self.assertEqual(alg['dimension']['total'], 8)

    def test_c2_oscillator_generators(self):
        """C(2) should have fermions and bosons keys."""
        gen = CnGenerator(1)
        schema = gen.to_json()
        osc = schema['oscillator_generators']

        self.assertIn('fermions', osc)
        self.assertIn('bosons', osc)
        self.assertEqual(osc['fermions']['labels'], ['a_1_p', 'a_1_m'])
        self.assertEqual(osc['bosons']['labels'], ['b_1_p', 'b_1_m'])

    def test_c2_central_elements(self):
        """C(2) should have central_elements key with kappa and K."""
        gen = CnGenerator(1)
        schema = gen.to_json()
        ce = schema['central_elements']

        self.assertIn('kappa', ce)
        self.assertIn('K', ce)
        self.assertEqual(ce['kappa']['parity'], 1)
        self.assertEqual(ce['K']['parity'], 0)

    def test_c2_basis(self):
        """C(2) basis should match expected generators."""
        gen = CnGenerator(1)
        schema = gen.to_json()
        basis = schema['basis']

        self.assertEqual(basis['even'], gen.basis_even)
        self.assertEqual(basis['odd'], gen.basis_odd)

    def test_c3_basis_count(self):
        """C(3) basis should have 11 even + 8 odd."""
        gen = CnGenerator(2)
        schema = gen.to_json()
        basis = schema['basis']

        self.assertEqual(len(basis['even']), 11)
        self.assertEqual(len(basis['odd']), 8)

    def test_oscillator_relations_structure(self):
        """oscillator_relations should have required keys."""
        gen = CnGenerator(1)
        schema = gen.to_json()
        osc_rel = schema['oscillator_relations']

        required_keys = [
            'standard_fermion_anticommutators',
            'bosonic_commutators',
            'mixed_commutators'
        ]
        for key in required_keys:
            self.assertIn(key, osc_rel, f"Missing key: {key}")

    def test_generator_realization_structure(self):
        """generator_realization should include C(2) basic generators."""
        gen = CnGenerator(1)
        schema = gen.to_json()
        real = schema['generator_realization']

        # Check that key generators are realized
        self.assertIn('H_1', real['realizations'])
        self.assertIn('H_2', real['realizations'])
        self.assertIn('E_eps_del1_pp', real['realizations'])


class TestCnGeneratorConsistency(unittest.TestCase):
    """Test consistency across all generators."""

    def test_all_generators_have_parity(self):
        """All generators should have a parity assignment."""
        for n in [1, 2, 3]:
            gen = CnGenerator(n)
            all_gens = gen.basis_even + gen.basis_odd
            for g in all_gens:
                self.assertIn(g, gen.parity, f"{g} missing parity for n={n}")

    def test_parity_matches_basis(self):
        """Parity should match basis classification."""
        for n in [1, 2, 3]:
            gen = CnGenerator(n)
            for g in gen.basis_even:
                self.assertEqual(gen.parity[g], 0, f"Even generator {g} should have parity 0")
            for g in gen.basis_odd:
                self.assertEqual(gen.parity[g], 1, f"Odd generator {g} should have parity 1")

    def test_json_parity_matches_basis(self):
        """JSON parity field should match basis."""
        for n in [1, 2, 3]:
            gen = CnGenerator(n)
            schema = gen.to_json()

            for g in schema['basis']['even']:
                self.assertEqual(schema['parity'][g], 0)
            for g in schema['basis']['odd']:
                self.assertEqual(schema['parity'][g], 1)


if __name__ == '__main__':
    unittest.main()
