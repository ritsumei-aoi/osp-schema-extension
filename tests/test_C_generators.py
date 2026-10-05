#!/usr/bin/env python3
"""
Unit tests for C(n+1) generator.

Tests:
- Parity consistency
- Dimension formulas
- Generator counts
- Basis structure consistency
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from C_generators import CGenerator, generate_schema1


def test_dimensions():
    """Test dimension formula: even = 2n^2 + n + 1, odd = 4n."""
    for n in [1, 2, 3]:
        gen = CGenerator(n)
        dims = gen.get_dimensions()

        expected_even = 2 * n**2 + n + 1
        expected_odd = 4 * n
        expected_total = expected_even + expected_odd

        assert dims['even'] == expected_even, f"n={n}: even dim {dims['even']} != {expected_even}"
        assert dims['odd'] == expected_odd, f"n={n}: odd dim {dims['odd']} != {expected_odd}"
        assert dims['total'] == expected_total, f"n={n}: total dim {dims['total']} != {expected_total}"

        print(f"✓ C({n+1}): even={dims['even']}, odd={dims['odd']}, total={dims['total']}")


def test_parity_consistency():
    """Test that all basis elements have correct parity."""
    for n in [1, 2, 3]:
        gen = CGenerator(n)
        even_basis, odd_basis = gen.get_basis()

        # All even basis should have parity 0
        for gen_label in even_basis:
            parity = gen.parity_map[gen_label]
            assert parity == 0, f"Even generator {gen_label} has parity {parity}"

        # All odd basis should have parity 1
        for gen_label in odd_basis:
            parity = gen.parity_map[gen_label]
            assert parity == 1, f"Odd generator {gen_label} has parity {parity}"

        print(f"✓ C({n+1}): parity consistency verified")


def test_generator_counts():
    """Test Cartan count and root count."""
    for n in [1, 2, 3]:
        gen = CGenerator(n)
        even_basis, odd_basis = gen.get_basis()

        # Count Cartan elements (should be n+1)
        cartan_count = len([g for g in even_basis if g.startswith('H_')])
        assert cartan_count == n + 1, f"n={n}: Cartan count {cartan_count} != {n+1}"

        # Verify odd count matches 4n
        assert len(odd_basis) == 4 * n, f"n={n}: odd count {len(odd_basis)} != {4*n}"

        print(f"✓ C({n+1}): Cartan={cartan_count}, odd={len(odd_basis)}")


def test_schema_generation():
    """Test complete schema generation."""
    for n in [1, 2, 3]:
        schema = generate_schema1(n)

        # Check top-level keys
        required_keys = ['schema_version', 'algebra', 'oscillator_generators',
                        'oscillator_relations', 'basis', 'parity',
                        'generator_realization', 'structure_constants',
                        'central_elements', 'metadata']

        for key in required_keys:
            assert key in schema, f"Missing key: {key}"

        # Check algebra field
        assert schema['algebra']['family'] == 'C'
        assert schema['algebra']['m'] == 1
        assert schema['algebra']['n'] == n

        # Check central elements
        assert len(schema['central_elements']) == 2
        labels = [ce['label'] for ce in schema['central_elements']]
        assert 'kappa' in labels
        assert 'K' in labels

        # Check parity consistency
        for gen_label, parity in schema['parity'].items():
            assert parity in [0, 1], f"Invalid parity for {gen_label}: {parity}"

        print(f"✓ C({n+1}): schema generation successful, keys verified")


def test_oscillator_realization_format():
    """Test generator realization format."""
    for n in [1, 2, 3]:
        gen = CGenerator(n)
        realizations = gen.generate_realizations()

        # Check all basis elements have realizations
        even_basis, odd_basis = gen.get_basis()
        all_basis = even_basis + odd_basis

        for label in all_basis:
            assert label in realizations, f"Missing realization for {label}"
            real = realizations[label]

            # Check required fields
            assert 'standard_form' in real
            assert 'frappat_form' in real
            assert 'parity' in real

            # Check standard_form is a list of dicts with 'words' and 'coeff'
            assert isinstance(real['standard_form'], list)
            for term in real['standard_form']:
                assert 'words' in term
                assert 'coeff' in term

        print(f"✓ C({n+1}): realization format verified")


if __name__ == '__main__':
    print("Running C(n+1) generator tests...\n")

    test_dimensions()
    print()

    test_parity_consistency()
    print()

    test_generator_counts()
    print()

    test_schema_generation()
    print()

    test_oscillator_realization_format()
    print()

    print("All tests passed! ✓")
