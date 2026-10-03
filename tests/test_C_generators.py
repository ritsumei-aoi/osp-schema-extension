"""Tests for C(n+1) structure constant generator."""

import json
import os
import sys
import pytest
from fractions import Fraction

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from C_generators import CnPlus1, generate_all, FERMION_OPS, has_fermionic_square, normal_order_word


class TestOscillatorAlgebra:
    def test_fermionic_square_detection(self):
        assert has_fermionic_square(['a_1_p', 'a_1_p']) is True
        assert has_fermionic_square(['a_1_m', 'a_1_m']) is True
        assert has_fermionic_square(['a_1_p', 'a_1_m']) is False
        assert has_fermionic_square(['b_1_p', 'b_1_p']) is False

    def test_normal_order_fermion_swap(self):
        """a_1_m * a_1_p = 1 - a_1_p * a_1_m"""
        osc_idx = {'a_1_p': 0, 'a_1_m': 1}
        result = normal_order_word(['a_1_m', 'a_1_p'], osc_idx)
        assert result.get(('a_1_p', 'a_1_m'), 0) == Fraction(-1)
        assert result.get((), 0) == Fraction(1)

    def test_normal_order_boson_swap(self):
        """b_k_m * b_k_p = b_k_p * b_k_m + 1"""
        osc_idx = {'b_1_p': 0, 'b_1_m': 1}
        result = normal_order_word(['b_1_m', 'b_1_p'], osc_idx)
        assert result.get(('b_1_p', 'b_1_m'), 0) == Fraction(1)
        assert result.get((), 0) == Fraction(1)

    def test_fermionic_square_is_zero(self):
        """(a_1^+)^2 = 0"""
        osc_idx = {'a_1_p': 0, 'a_1_m': 1}
        result = normal_order_word(['a_1_p', 'a_1_p'], osc_idx)
        assert result == {}

    def test_boson_commute_different_modes(self):
        """b_1_m * b_2_p = b_2_p * b_1_m (free swap, no delta)"""
        osc_idx = {'b_1_p': 0, 'b_1_m': 1, 'b_2_p': 2, 'b_2_m': 3}
        result = normal_order_word(['b_1_m', 'b_2_p'], osc_idx)
        # b_1_m (idx 1) > b_2_p (idx 2)? No: 1 < 2, so already in order!
        # Wait: in this simple 4-element index: b_1_p=0, b_1_m=1, b_2_p=2, b_2_m=3.
        # b_1_m has idx 1, b_2_p has idx 2. 1 < 2 so (b_1_m, b_2_p) IS in order.
        assert result == {('b_1_m', 'b_2_p'): Fraction(1)}


class TestCnPlus1Basis:
    @pytest.mark.parametrize("n,expected_even,expected_odd,expected_total", [
        (1, 4, 4, 8),
        (2, 11, 8, 19),
        (3, 22, 12, 34),
    ])
    def test_basis_counts(self, n, expected_even, expected_odd, expected_total):
        alg = CnPlus1(n)
        assert len(alg.even_basis) == expected_even, f"n={n}: even count"
        assert len(alg.odd_basis) == expected_odd, f"n={n}: odd count"
        assert len(alg.basis) == expected_total, f"n={n}: total count"

    def test_parity_consistency(self):
        for n in range(1, 4):
            alg = CnPlus1(n)
            for g in alg.even_basis:
                assert alg.parity_map[g] == 0, f"n={n}: {g} should be even"
            for g in alg.odd_basis:
                assert alg.parity_map[g] == 1, f"n={n}: {g} should be odd"

    def test_no_duplicates(self):
        for n in range(1, 4):
            alg = CnPlus1(n)
            assert len(set(alg.basis)) == len(alg.basis), f"n={n}: duplicate basis elements"

    def test_all_generators_have_realizations(self):
        for n in range(1, 4):
            alg = CnPlus1(n)
            for g in alg.basis:
                assert g in alg.realizations, f"n={n}: missing realization for {g}"


class TestCartan:
    def test_H1_eigenvalues_n1(self):
        """[H_1, E_eps1_del1_pp] = 2 * E_eps1_del1_pp for C(2)."""
        alg = CnPlus1(1)
        from C_generators import graded_bracket
        bracket = graded_bracket(
            alg.realizations['H_1'],
            alg.realizations['E_eps1_del1_pp'],
            0, 1, alg.osc_idx
        )
        decomp = alg.decompose(bracket)
        assert decomp == {'E_eps1_del1_pp': Fraction(2)}, f"Got {decomp}"

    def test_H1_eigenvalues_cross(self):
        """[H_1, E_eps1_del2_pp] = 1 * E_eps1_del2_pp for C(3) (δ_1 contributes 0)."""
        alg = CnPlus1(2)
        from C_generators import graded_bracket
        bracket = graded_bracket(
            alg.realizations['H_1'],
            alg.realizations['E_eps1_del2_pp'],
            0, 1, alg.osc_idx
        )
        decomp = alg.decompose(bracket)
        # E_eps1_del2_pp = a_1^+ b_2^+, H_1 = N_a + N_{b_1}
        # [H_1, a_1^+ b_2^+] = 1 (from N_a contrib.) + 0 (b_1 doesn't touch b_2^+) = 1
        assert decomp == {'E_eps1_del2_pp': Fraction(1)}, f"Got {decomp}"

    def test_anticommutator_pp_mm(self):
        """{E_eps1_del1_pp, E_eps1_del1_mm} should be a Cartan element."""
        alg = CnPlus1(1)
        from C_generators import graded_bracket
        bracket = graded_bracket(
            alg.realizations['E_eps1_del1_pp'],
            alg.realizations['E_eps1_del1_mm'],
            1, 1, alg.osc_idx
        )
        decomp = alg.decompose(bracket)
        # From analysis: = -H_1 - 2*H_2 for n=1
        assert 'H_1' in decomp or 'H_2' in decomp, f"Should be Cartan, got {decomp}"
        # Verify it's purely Cartan
        for k in decomp:
            assert k.startswith('H_'), f"Non-Cartan term {k} in {decomp}"


class TestStructureConstants:
    @pytest.fixture(scope='class')
    def schemas(self):
        return {n: CnPlus1(n).to_schema1_json() for n in range(1, 4)}

    def test_schema_version(self, schemas):
        for n, s in schemas.items():
            assert s['schema_version'] == '5.0'

    def test_algebra_fields(self, schemas):
        for n, s in schemas.items():
            assert s['algebra']['family'] == 'C'
            assert s['algebra']['m'] == 1
            assert s['algebra']['n'] == n
            dim = s['algebra']['dimension']
            assert dim['even'] == 2 * n * n + n + 1
            assert dim['odd'] == 4 * n
            assert dim['total'] == 2 * n * n + 5 * n + 1

    def test_central_elements_present(self, schemas):
        for n, s in schemas.items():
            assert 'central_elements' in s
            assert 'kappa' in s['central_elements']
            assert 'K' in s['central_elements']
            assert s['central_elements']['kappa']['parity'] == 1
            assert s['central_elements']['K']['parity'] == 0

    def test_structure_constants_not_empty(self, schemas):
        for n, s in schemas.items():
            sc = s['structure_constants']
            assert len(sc) > 0, f"n={n}: no structure constants"
            # n=1: C(2) should have some brackets
            # n=2: C(3) should have more

    def test_structure_constants_basis_labels(self, schemas):
        """All X, Y, Z in structure constants must be valid basis elements."""
        for n, s in schemas.items():
            alg = CnPlus1(n)
            basis_set = set(alg.basis)
            for entry in s['structure_constants']:
                assert entry['X'] in basis_set, f"n={n}: X={entry['X']} not in basis"
                assert entry['Y'] in basis_set, f"n={n}: Y={entry['Y']} not in basis"
                assert entry['Z'] in basis_set, f"n={n}: Z={entry['Z']} not in basis"

    def test_x_before_y_in_basis(self, schemas):
        """By convention, X appears before Y in basis ordering."""
        for n, s in schemas.items():
            alg = CnPlus1(n)
            basis_idx = {g: i for i, g in enumerate(alg.basis)}
            for entry in s['structure_constants']:
                ix = basis_idx[entry['X']]
                iy = basis_idx[entry['Y']]
                assert ix < iy, f"n={n}: X={entry['X']}({ix}) not before Y={entry['Y']}({iy})"

    def test_coeff_parseable(self, schemas):
        """All coefficients should be parseable as Fraction."""
        for n, s in schemas.items():
            for entry in s['structure_constants']:
                Fraction(entry['coeff'])


class TestJSONOutput:
    def test_json_files_created(self, tmp_path):
        generate_all(str(tmp_path))
        for n in range(1, 4):
            fname = tmp_path / f'C_{n}_structure.json'
            assert fname.exists(), f"C_{n}_structure.json not created"

    def test_json_valid(self, tmp_path):
        generate_all(str(tmp_path))
        for n in range(1, 4):
            fname = tmp_path / f'C_{n}_structure.json'
            with open(fname) as f:
                data = json.load(f)
            assert data['schema_version'] == '5.0'
