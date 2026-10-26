#!/usr/bin/env python3
"""
test_C_generators.py: Unit tests for C(n+1) structure constant generator.
"""

import pytest
import sys
import os
from fractions import Fraction
from itertools import combinations

sys.path.insert(0, os.path.dirname(__file__))
from C_generators import (
    osc_labels, normalize, graded_bracket, build_generators,
    decompose, compute_structure_constants, build_schema, is_fermionic,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def bracket_coeffs(n, lbl_i, lbl_j):
    """Compute [lbl_i, lbl_j} and return decomposed coefficient dict."""
    even, odd, gens = build_generators(n)
    all_labels = even + odd
    order = osc_labels(n)
    poly_i, par_i = gens[lbl_i]
    poly_j, par_j = gens[lbl_j]
    result = graded_bracket(poly_i, poly_j, par_i, par_j, order)
    if not result:
        return {lbl: Fraction(0) for lbl in all_labels}
    return decompose(result, all_labels, gens)


def nonzero(coeffs):
    return {k: v for k, v in coeffs.items() if v != 0}


# ---------------------------------------------------------------------------
# 1. Oscillator normalization
# ---------------------------------------------------------------------------

class TestNormalize:
    def test_already_normal(self):
        order = osc_labels(1)
        assert normalize(('a_1_p', 'b_1_p'), order) == {('a_1_p', 'b_1_p'): Fraction(1)}

    def test_fermionic_repeat_zero(self):
        order = osc_labels(1)
        assert normalize(('a_1_p', 'a_1_p'), order) == {}

    def test_fermionic_swap(self):
        # a_1_m a_1_p = -a_1_p a_1_m + 1
        order = osc_labels(1)
        result = normalize(('a_1_m', 'a_1_p'), order)
        assert result.get(('a_1_p', 'a_1_m'), 0) == Fraction(-1)
        assert result.get((), 0) == Fraction(1)

    def test_bosonic_swap(self):
        # b_k_m b_k_p = b_k_p b_k_m + 1
        order = osc_labels(1)
        result = normalize(('b_1_m', 'b_1_p'), order)
        assert result.get(('b_1_p', 'b_1_m'), 0) == Fraction(1)
        assert result.get((), 0) == Fraction(1)

    def test_mixed_commutes(self):
        # b_1_p a_1_p → a_1_p b_1_p (no commutator)
        order = osc_labels(1)
        result = normalize(('b_1_p', 'a_1_p'), order)
        assert result == {('a_1_p', 'b_1_p'): Fraction(1)}

    def test_different_bosons_no_comm(self):
        # b_1_m b_2_p: b_1_m (idx 3) < b_2_p (idx 4) for n=2 → already ordered
        order = osc_labels(2)
        result = normalize(('b_1_m', 'b_2_p'), order)
        assert result == {('b_1_m', 'b_2_p'): Fraction(1)}

    def test_empty_word(self):
        order = osc_labels(1)
        assert normalize((), order) == {(): Fraction(1)}


# ---------------------------------------------------------------------------
# 2. Generator counts and parity
# ---------------------------------------------------------------------------

class TestGeneratorCounts:
    @pytest.mark.parametrize('n', [1, 2, 3])
    def test_even_dim(self, n):
        even, odd, _ = build_generators(n)
        assert len(even) == 2*n*n + n + 1

    @pytest.mark.parametrize('n', [1, 2, 3])
    def test_odd_dim(self, n):
        even, odd, _ = build_generators(n)
        assert len(odd) == 4 * n

    @pytest.mark.parametrize('n', [1, 2, 3])
    def test_total_dim(self, n):
        even, odd, _ = build_generators(n)
        assert len(even) + len(odd) == 2*n*n + 5*n + 1

    @pytest.mark.parametrize('n', [1, 2, 3])
    def test_parity_even(self, n):
        even, _, gens = build_generators(n)
        for lbl in even:
            assert gens[lbl][1] == 0, f'{lbl} should be even'

    @pytest.mark.parametrize('n', [1, 2, 3])
    def test_parity_odd(self, n):
        _, odd, gens = build_generators(n)
        for lbl in odd:
            assert gens[lbl][1] == 1, f'{lbl} should be odd'

    @pytest.mark.parametrize('n', [1, 2, 3])
    def test_no_duplicate_labels(self, n):
        even, odd, _ = build_generators(n)
        all_labels = even + odd
        assert len(all_labels) == len(set(all_labels))


# ---------------------------------------------------------------------------
# 3. Known bracket values (hand-computed, n=1)
# ---------------------------------------------------------------------------

class TestKnownBracketsN1:
    """For C(2) = osp(2|2), n=1."""

    def test_H1_E_eps1_del1_pp(self):
        # [H_1, E_{ε+δ_1}] = 2 E_{ε+δ_1}
        coeffs = bracket_coeffs(1, 'H_1', 'E_eps1_del1_pp')
        assert nonzero(coeffs) == {'E_eps1_del1_pp': Fraction(2)}

    def test_H2_E_eps1_del1_pp(self):
        # [H_2, E_{ε+δ_1}] = -1·E (H_2 = -N_{b1} - 1/2 for n=1)
        coeffs = bracket_coeffs(1, 'H_2', 'E_eps1_del1_pp')
        assert nonzero(coeffs) == {'E_eps1_del1_pp': Fraction(-1)}

    def test_H1_E_eps1_del1_pm(self):
        # [H_1, E_{ε-δ_1}] = 0·E (H_1 = N_{a1}+N_{b1}; E = a_1_p b_1_m; eigenvalue = 1 - 1 = 0)
        coeffs = bracket_coeffs(1, 'H_1', 'E_eps1_del1_pm')
        assert nonzero(coeffs) == {}

    def test_H1_E_eps1_del1_mp(self):
        # [H_1, E_{-ε+δ_1}] = 0 (eigenvalue = -1 + 1 = 0)
        coeffs = bracket_coeffs(1, 'H_1', 'E_eps1_del1_mp')
        assert nonzero(coeffs) == {}

    def test_H1_E_eps1_del1_mm(self):
        # [H_1, E_{-ε-δ_1}] = -2·E (eigenvalue = -1 - 1 = -2)
        coeffs = bracket_coeffs(1, 'H_1', 'E_eps1_del1_mm')
        assert nonzero(coeffs) == {'E_eps1_del1_mm': Fraction(-2)}

    def test_E2del1p_E2del1m(self):
        # [E_{2δ1}_p, E_{2δ1}_m] = H_{n+1} = H_2 for n=1
        coeffs = bracket_coeffs(1, 'E_2del1_p', 'E_2del1_m')
        assert nonzero(coeffs) == {'H_2': Fraction(1)}

    def test_Epp_Emp_gives_E2del1p(self):
        # {E_{ε+δ1}, E_{-ε+δ1}} = (b_1_p)^2 = 2 E_{2δ1}_p
        coeffs = bracket_coeffs(1, 'E_eps1_del1_pp', 'E_eps1_del1_mp')
        assert nonzero(coeffs) == {'E_2del1_p': Fraction(2)}

    def test_Epm_Emm_gives_E2del1m(self):
        # {E_{ε-δ1}, E_{-ε-δ1}} = (b_1_m)^2 = 2 E_{2δ1}_m
        coeffs = bracket_coeffs(1, 'E_eps1_del1_pm', 'E_eps1_del1_mm')
        assert nonzero(coeffs) == {'E_2del1_m': Fraction(2)}

    def test_Epp_Epm_zero(self):
        # {E_{ε+δ1}, E_{ε-δ1}}: both have a_1_p → a_1_p^2 = 0
        coeffs = bracket_coeffs(1, 'E_eps1_del1_pp', 'E_eps1_del1_pm')
        assert nonzero(coeffs) == {}

    def test_Emp_Emm_zero(self):
        # {E_{-ε+δ1}, E_{-ε-δ1}}: both have a_1_m → a_1_m^2 = 0
        coeffs = bracket_coeffs(1, 'E_eps1_del1_mp', 'E_eps1_del1_mm')
        assert nonzero(coeffs) == {}

    def test_Epp_Emm_gives_cartans(self):
        # {E_{ε+δ1}, E_{-ε-δ1}} should land in Cartan span
        coeffs = bracket_coeffs(1, 'E_eps1_del1_pp', 'E_eps1_del1_mm')
        nz = nonzero(coeffs)
        for k in nz:
            assert k.startswith('H_'), f'Expected Cartan only, got {k}'

    def test_Epm_Emp_gives_cartans(self):
        # {E_{ε-δ1}, E_{-ε+δ1}} should land in Cartan span
        coeffs = bracket_coeffs(1, 'E_eps1_del1_pm', 'E_eps1_del1_mp')
        nz = nonzero(coeffs)
        for k in nz:
            assert k.startswith('H_'), f'Expected Cartan only, got {k}'

    def test_Cartans_commute(self):
        # [H_1, H_2] = 0
        coeffs = bracket_coeffs(1, 'H_1', 'H_2')
        assert nonzero(coeffs) == {}

    def test_even_selfbracket_zero(self):
        # [X, X} = 0 for even X
        for lbl in ['H_1', 'H_2', 'E_2del1_p', 'E_2del1_m']:
            coeffs = bracket_coeffs(1, lbl, lbl)
            assert nonzero(coeffs) == {}, f'[{lbl},{lbl}] should be 0'


# ---------------------------------------------------------------------------
# 4. Graded antisymmetry: [Y,X} = -(-1)^(pX pY) [X,Y}
# ---------------------------------------------------------------------------

class TestGradedAntisymmetry:
    @pytest.mark.parametrize('n', [1, 2])
    def test_antisymmetry_even_even(self, n):
        """[H_1, E_2del1_p} = -[E_2del1_p, H_1}"""
        even, odd, gens = build_generators(n)
        all_labels = even + odd
        order = osc_labels(n)

        for xi, xj in [('H_1', 'E_2del1_p'), ('H_1', f'H_{n+1}')]:
            pi_x, pi_y = gens[xi][1], gens[xj][1]
            b_xy = graded_bracket(gens[xi][0], gens[xj][0], pi_x, pi_y, order)
            b_yx = graded_bracket(gens[xj][0], gens[xi][0], pi_y, pi_x, order)
            sign = (-1) ** (pi_x * pi_y)
            # [Y,X} should equal -sign * [X,Y}
            expected = {w: -Fraction(sign) * c for w, c in b_xy.items()}
            from collections import defaultdict
            diff = defaultdict(Fraction)
            for w, c in b_yx.items():
                diff[w] += c
            for w, c in expected.items():
                diff[w] -= c
            diff = {k: v for k, v in diff.items() if v != 0}
            assert diff == {}, f'Antisymmetry failed for [{xi},{xj}]'

    @pytest.mark.parametrize('n', [1, 2])
    def test_antisymmetry_odd_odd(self, n):
        """For odd X,Y: {Y,X} = +{X,Y} (graded sym for two odd generators)."""
        even, odd, gens = build_generators(n)
        order = osc_labels(n)
        xi, xj = f'E_eps1_del1_pp', f'E_eps1_del1_mp'
        pi_x, pi_y = gens[xi][1], gens[xj][1]
        b_xy = graded_bracket(gens[xi][0], gens[xj][0], pi_x, pi_y, order)
        b_yx = graded_bracket(gens[xj][0], gens[xi][0], pi_y, pi_x, order)
        sign = (-1) ** (pi_x * pi_y)  # = (-1)^1 = -1
        from collections import defaultdict
        diff = defaultdict(Fraction)
        for w, c in b_yx.items():
            diff[w] += c
        for w, c in b_xy.items():
            diff[w] -= Fraction(-sign) * c
        diff = {k: v for k, v in diff.items() if v != 0}
        assert diff == {}


# ---------------------------------------------------------------------------
# 5. Jacobi identity (spot checks)
# ---------------------------------------------------------------------------

class TestJacobi:
    """
    Graded Jacobi: [[X,Y},Z} + (-1)^{p(Z)(p(X)+p(Y))} [[Y,Z},X} + (-1)^{p(X)(p(Y)+p(Z))} [[Z,X},Y} = 0
    Or equivalently: the sum of cyclic permutations with appropriate signs = 0.
    """

    def _poly_bracket(self, n, li, lj):
        even, odd, gens = build_generators(n)
        all_labels = even + odd
        order = osc_labels(n)
        pi, pj = gens[li][1], gens[lj][1]
        b = graded_bracket(gens[li][0], gens[lj][0], pi, pj, order)
        p_b = pi ^ pj  # parity of [li, lj} (for nonzero result)
        return b, p_b, gens, all_labels, order

    def _jacobi_check(self, n, lx, ly, lz):
        """
        Graded super Jacobi identity (cyclic form):
        (-1)^{p(x)p(z)} [[x,y},z} + (-1)^{p(y)p(x)} [[y,z},x} + (-1)^{p(z)p(y)} [[z,x},y} = 0
        """
        even, odd, gens = build_generators(n)
        order = osc_labels(n)
        px, py, pz = gens[lx][1], gens[ly][1], gens[lz][1]
        X, Y, Z = gens[lx][0], gens[ly][0], gens[lz][0]

        p_xy = (px + py) % 2
        p_yz = (py + pz) % 2
        p_zx = (pz + px) % 2

        XY = graded_bracket(X, Y, px, py, order)
        YZ = graded_bracket(Y, Z, py, pz, order)
        ZX = graded_bracket(Z, X, pz, px, order)

        # Signs for the cyclic Jacobi form
        s1 = (-1) ** (px * pz)   # for [[X,Y},Z}
        s2 = (-1) ** (py * px)   # for [[Y,Z},X}
        s3 = (-1) ** (pz * py)   # for [[Z,X},Y}

        XYZ = graded_bracket(XY, Z, p_xy, pz, order)
        YZX = graded_bracket(YZ, X, p_yz, px, order)
        ZXY = graded_bracket(ZX, Y, p_zx, py, order)

        from collections import defaultdict
        total = defaultdict(Fraction)
        for w, c in XYZ.items():
            total[w] += Fraction(s1) * c
        for w, c in YZX.items():
            total[w] += Fraction(s2) * c
        for w, c in ZXY.items():
            total[w] += Fraction(s3) * c

        return {k: v for k, v in total.items() if v != 0}

    @pytest.mark.parametrize('n', [1, 2])
    def test_jacobi_H1_H2_E(self, n):
        result = self._jacobi_check(n, 'H_1', f'H_{n+1}', 'E_eps1_del1_pp')
        assert result == {}, f'Jacobi failed (n={n}): {result}'

    @pytest.mark.parametrize('n', [1, 2])
    def test_jacobi_H1_Epp_Emm(self, n):
        result = self._jacobi_check(n, 'H_1', 'E_eps1_del1_pp', 'E_eps1_del1_mm')
        assert result == {}, f'Jacobi failed (n={n}): {result}'

    @pytest.mark.parametrize('n', [1, 2])
    def test_jacobi_Epp_Emp_E2p(self, n):
        result = self._jacobi_check(n, 'E_eps1_del1_pp', 'E_eps1_del1_mp', 'E_2del1_m')
        assert result == {}, f'Jacobi failed (n={n}): {result}'

    def test_jacobi_n2_cross_boson(self):
        """For n=2: test with a generator involving both δ_1 and δ_2."""
        result = self._jacobi_check(2, 'E_eps1_del1_pp', 'E_eps1_del2_mm', 'H_1')
        assert result == {}, f'Jacobi failed (n=2): {result}'

    def test_jacobi_n2_del_generators(self):
        result = self._jacobi_check(2, 'E_del1_del2_pp', 'E_eps1_del1_pm', 'H_2')
        assert result == {}, f'Jacobi failed (n=2): {result}'


# ---------------------------------------------------------------------------
# 6. Schema structure tests
# ---------------------------------------------------------------------------

class TestSchemaStructure:
    @pytest.mark.parametrize('n', [1, 2, 3])
    def test_schema_version(self, n):
        schema = build_schema(n)
        assert schema['schema_version'] == '5.0'

    @pytest.mark.parametrize('n', [1, 2, 3])
    def test_algebra_fields(self, n):
        schema = build_schema(n)
        alg = schema['algebra']
        assert alg['family'] == 'C'
        assert alg['m'] == 1
        assert alg['n'] == n
        assert alg['dimension']['even'] == 2*n*n + n + 1
        assert alg['dimension']['odd'] == 4 * n
        assert alg['dimension']['total'] == 2*n*n + 5*n + 1

    @pytest.mark.parametrize('n', [1, 2, 3])
    def test_central_elements_present(self, n):
        schema = build_schema(n)
        ce = schema['central_elements']
        assert 'K' in ce and ce['K']['parity'] == 0
        assert 'kappa' in ce and ce['kappa']['parity'] == 1

    @pytest.mark.parametrize('n', [1, 2, 3])
    def test_basis_counts(self, n):
        schema = build_schema(n)
        basis = schema['basis']
        assert len(basis['even']) == 2*n*n + n + 1
        assert len(basis['odd']) == 4 * n

    @pytest.mark.parametrize('n', [1, 2, 3])
    def test_parity_matches_basis(self, n):
        schema = build_schema(n)
        parity = schema['parity']
        for lbl in schema['basis']['even']:
            assert parity[lbl] == 0, f'{lbl} parity mismatch'
        for lbl in schema['basis']['odd']:
            assert parity[lbl] == 1, f'{lbl} parity mismatch'

    @pytest.mark.parametrize('n', [1, 2, 3])
    def test_structure_constants_reference_valid_generators(self, n):
        schema = build_schema(n)
        all_labels = set(schema['basis']['even'] + schema['basis']['odd'])
        for sc in schema['structure_constants']:
            assert sc['X'] in all_labels, f"SC X={sc['X']} not in basis"
            assert sc['Y'] in all_labels, f"SC Y={sc['Y']} not in basis"
            assert sc['Z'] in all_labels, f"SC Z={sc['Z']} not in basis"
            assert sc['coeff'] != '0'

    @pytest.mark.parametrize('n', [1, 2, 3])
    def test_structure_constants_nonzero(self, n):
        schema = build_schema(n)
        for sc in schema['structure_constants']:
            assert Fraction(sc['coeff']) != 0, f"Zero coefficient in SC: {sc}"

    @pytest.mark.parametrize('n', [1, 2, 3])
    def test_fermion_labels(self, n):
        schema = build_schema(n)
        ferm = schema['oscillator_generators']['fermions']
        assert ferm['labels'] == ['a_1_p', 'a_1_m']
        assert ferm['m'] == 1
        assert ferm['parity'] == 1
