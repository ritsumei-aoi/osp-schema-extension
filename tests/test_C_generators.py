#!/usr/bin/env python3
"""
Unit tests for C(n+1) structure constant generator.
"""

import sys
import os
import json
import unittest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from C_generators import CnPlus1Generator


class TestCnPlus1Dimensions(unittest.TestCase):
    """Test dimension calculations."""

    def test_c2_dimensions(self):
        """C(2) = osp(2|2) should have even=4, odd=4, total=8."""
        gen = CnPlus1Generator(1)
        self.assertEqual(gen.even_dim, 4)
        self.assertEqual(gen.odd_dim, 4)
        self.assertEqual(gen.total_dim, 8)

    def test_c3_dimensions(self):
        """C(3) = osp(2|4) should have even=11, odd=8, total=19."""
        gen = CnPlus1Generator(2)
        self.assertEqual(gen.even_dim, 11)
        self.assertEqual(gen.odd_dim, 8)
        self.assertEqual(gen.total_dim, 19)

    def test_c4_dimensions(self):
        """C(4) = osp(2|6) should have even=22, odd=12, total=34."""
        gen = CnPlus1Generator(3)
        self.assertEqual(gen.even_dim, 22)
        self.assertEqual(gen.odd_dim, 12)
        self.assertEqual(gen.total_dim, 34)

    def test_dimension_formula(self):
        """Test dimension formula: even=2n^2+n+1, odd=4n."""
        for n in range(1, 5):
            gen = CnPlus1Generator(n)
            expected_even = 2*n*n + n + 1
            expected_odd = 4*n
            self.assertEqual(gen.even_dim, expected_even,
                           f"Even dimension mismatch for n={n}")
            self.assertEqual(gen.odd_dim, expected_odd,
                           f"Odd dimension mismatch for n={n}")


class TestCnPlus1Basis(unittest.TestCase):
    """Test basis generation."""

    def test_basis_sizes(self):
        """Test that basis lists have correct sizes."""
        for n in range(1, 4):
            gen = CnPlus1Generator(n)
            even, odd, parity = gen.build_basis()
            self.assertEqual(len(even), gen.even_dim,
                           f"Even basis size mismatch for n={n}")
            self.assertEqual(len(odd), gen.odd_dim,
                           f"Odd basis size mismatch for n={n}")

    def test_basis_completeness(self):
        """Test that all basis elements are in parity dict."""
        for n in range(1, 4):
            gen = CnPlus1Generator(n)
            even, odd, parity = gen.build_basis()
            for elem in even + odd:
                self.assertIn(elem, parity,
                            f"Missing parity for {elem}")

    def test_parity_values(self):
        """Test that parities are correct."""
        for n in range(1, 4):
            gen = CnPlus1Generator(n)
            even, odd, parity = gen.build_basis()

            # Even elements should have parity 0
            for elem in even:
                self.assertEqual(parity[elem], 0,
                               f"Wrong parity for even element {elem}")

            # Odd elements should have parity 1
            for elem in odd:
                self.assertEqual(parity[elem], 1,
                               f"Wrong parity for odd element {elem}")

    def test_basis_ordering(self):
        """Test that basis respects PBW ordering."""
        for n in range(1, 4):
            gen = CnPlus1Generator(n)
            even, odd, parity = gen.build_basis()

            # Odd basis should come before even (in concatenation order)
            # Combined PBW ordering: κ < [odd] < [even]
            all_basis = odd + even

            # Check that all odd elements appear before even
            last_odd_idx = -1
            first_even_idx = len(all_basis)

            for i, elem in enumerate(all_basis):
                if parity[elem] == 1:
                    last_odd_idx = i
                elif first_even_idx == len(all_basis) and parity[elem] == 0:
                    first_even_idx = i

            if last_odd_idx >= 0 and first_even_idx < len(all_basis):
                self.assertLess(last_odd_idx, first_even_idx,
                              "Odd elements should come before even in PBW ordering")

    def test_no_duplicate_basis_elements(self):
        """Test that basis has no duplicates."""
        for n in range(1, 4):
            gen = CnPlus1Generator(n)
            even, odd, parity = gen.build_basis()

            all_basis = even + odd
            self.assertEqual(len(all_basis), len(set(all_basis)),
                           "Duplicate basis elements found")


class TestCnPlus1Schema(unittest.TestCase):
    """Test schema generation."""

    def test_schema_top_level_keys(self):
        """Test that schema has all required top-level keys."""
        gen = CnPlus1Generator(1)
        schema = gen.generate_schema()

        required_keys = [
            'schema_version', 'algebra', 'central_elements',
            'oscillator_generators', 'oscillator_relations',
            'basis', 'parity', 'generator_realization',
            'structure_constants', 'metadata'
        ]

        for key in required_keys:
            self.assertIn(key, schema, f"Missing key: {key}")

    def test_schema_version(self):
        """Test schema version."""
        gen = CnPlus1Generator(1)
        schema = gen.generate_schema()
        self.assertEqual(schema['schema_version'], '5.0')

    def test_algebra_field(self):
        """Test algebra field."""
        for n in range(1, 4):
            gen = CnPlus1Generator(n)
            schema = gen.generate_schema()
            alg = schema['algebra']

            self.assertEqual(alg['family'], 'C')
            self.assertEqual(alg['m'], 1)
            self.assertEqual(alg['n'], n)
            self.assertEqual(alg['dimension']['even'], 2*n*n + n + 1)
            self.assertEqual(alg['dimension']['odd'], 4*n)

    def test_central_elements_structure(self):
        """Test central_elements key."""
        gen = CnPlus1Generator(1)
        schema = gen.generate_schema()
        ce = schema['central_elements']

        # Should have kappa and K
        self.assertIn('kappa', ce)
        self.assertIn('K', ce)

        # kappa should be odd
        self.assertEqual(ce['kappa']['parity'], 1)

        # K should be even
        self.assertEqual(ce['K']['parity'], 0)

    def test_basis_consistency_with_dimensions(self):
        """Test that basis size matches dimension."""
        for n in range(1, 4):
            gen = CnPlus1Generator(n)
            schema = gen.generate_schema()

            self.assertEqual(
                len(schema['basis']['even']),
                schema['algebra']['dimension']['even']
            )
            self.assertEqual(
                len(schema['basis']['odd']),
                schema['algebra']['dimension']['odd']
            )

    def test_parity_consistency(self):
        """Test that parity dict matches basis elements."""
        for n in range(1, 4):
            gen = CnPlus1Generator(n)
            schema = gen.generate_schema()

            parity = schema['parity']
            all_basis = schema['basis']['even'] + schema['basis']['odd']

            # All basis elements should have parity entry
            for elem in all_basis:
                self.assertIn(elem, parity,
                            f"Missing parity for {elem}")

            # Parity values should match basis lists
            for elem in schema['basis']['even']:
                self.assertEqual(parity[elem], 0,
                               f"Wrong parity for even element {elem}")

            for elem in schema['basis']['odd']:
                self.assertEqual(parity[elem], 1,
                               f"Wrong parity for odd element {elem}")

    def test_generator_realization_coverage(self):
        """Test that generator_realization has entries for basis elements."""
        for n in range(1, 4):
            gen = CnPlus1Generator(n)
            schema = gen.generate_schema()

            realizations = schema['generator_realization']['realizations']

            # At minimum, Cartan elements should be present
            for i in range(1, n + 2):
                self.assertIn(f"H_{i}", realizations,
                            f"Missing realization for H_{i}")

    def test_oscillator_generators_structure(self):
        """Test oscillator_generators key."""
        gen = CnPlus1Generator(1)
        schema = gen.generate_schema()
        og = schema['oscillator_generators']

        # Should have fermions and bosons
        self.assertIn('fermions', og)
        self.assertIn('bosons', og)

        # Fermions should have labels a_1_p, a_1_m
        self.assertEqual(og['fermions']['count'], 2)
        self.assertIn('a_1_p', og['fermions']['labels'])
        self.assertIn('a_1_m', og['fermions']['labels'])

    def test_json_serializable(self):
        """Test that schema can be JSON serialized."""
        for n in range(1, 4):
            gen = CnPlus1Generator(n)
            schema = gen.generate_schema()

            # Should not raise an exception
            json_str = json.dumps(schema)
            self.assertIsInstance(json_str, str)

            # Should be deserializable
            deserialized = json.loads(json_str)
            self.assertEqual(deserialized['algebra']['n'], n)


class TestCnPlus1StructureConstants(unittest.TestCase):
    """Test structure constants."""

    def test_structure_constants_format(self):
        """Test that structure constants have correct format."""
        gen = CnPlus1Generator(1)
        schema = gen.generate_schema()
        scs = schema['structure_constants']

        for sc in scs:
            # Each structure constant should have X, Y, Z, coeff, sign_rule
            self.assertIn('X', sc)
            self.assertIn('Y', sc)
            self.assertIn('Z', sc)
            self.assertIn('coeff', sc)
            self.assertIn('sign_rule', sc)

    def test_structure_constants_not_empty(self):
        """Test that structure constants are non-empty."""
        for n in range(1, 4):
            gen = CnPlus1Generator(n)
            schema = gen.generate_schema()
            scs = schema['structure_constants']

            self.assertGreater(len(scs), 0,
                             f"Structure constants empty for n={n}")


if __name__ == '__main__':
    unittest.main()
