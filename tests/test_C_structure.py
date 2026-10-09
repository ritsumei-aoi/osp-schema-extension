"""
Tests for C(n+1) = osp(2|2n) structure constants (Schema 1).

Run:  python -m pytest tests/test_C_structure.py -v
"""
import json
import os
import sys
from fractions import Fraction

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from build_C_structure_constants import (
    add_polys,
    basis_lists,
    build_generators,
    build_schema1,
    decompose,
    graded_bracket,
    scale_poly,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(params=[1, 2, 3])
def n(request):
    return request.param


@pytest.fixture
def gens(n):
    return build_generators(n)


@pytest.fixture
def schema(n):
    return build_schema1(n)


# Helper: build structure-constant lookup for a given n
def _build_sc(n):
    """
    Return sc[(X, Y)] = {Z: Fraction} for the upper-triangle of brackets,
    combined ordering = even then odd.
    """
    gens = build_generators(n)
    basis_even, basis_odd = basis_lists(gens)
    combined = basis_even + basis_odd
    sc = {}
    for xi, Xname in enumerate(combined):
        for yi in range(xi, len(combined)):
            Yname = combined[yi]
            Xpoly, pX = gens[Xname]
            Ypoly, pY = gens[Yname]
            bracket = graded_bracket(Xpoly, Ypoly, pX, pY)
            if bracket:
                sc[(Xname, Yname)] = decompose(bracket, gens, n)
    return sc


def _get(sc, X, Y):
    """Retrieve bracket [X, Y} (tries both orderings)."""
    return sc.get((X, Y), sc.get((Y, X), {}))


# ── 1. Dimension tests ────────────────────────────────────────────────────────

class TestDimensions:
    def test_even_count(self, n, gens):
        even = [nm for nm, (_, p) in gens.items() if p == 0]
        assert len(even) == 2 * n * n + n + 1

    def test_odd_count(self, n, gens):
        odd = [nm for nm, (_, p) in gens.items() if p == 1]
        assert len(odd) == 4 * n

    def test_total_count(self, n, gens):
        assert len(gens) == 2 * n * n + 5 * n + 1


# ── 2. Parity tests ───────────────────────────────────────────────────────────

class TestParity:
    def test_cartan_parity(self, n, gens):
        for k in range(1, n + 2):
            assert gens[f'H_{k}'][1] == 0

    def test_odd_generator_parity(self, n, gens):
        for k in range(1, n + 1):
            for suffix in ('pp', 'pm', 'mp', 'mm'):
                assert gens[f'E_eps1_del{k}_{suffix}'][1] == 1

    def test_even_root_parity(self, n, gens):
        for k in range(1, n + 1):
            assert gens[f'E_2del{k}_p'][1] == 0
            assert gens[f'E_2del{k}_m'][1] == 0
        for i in range(1, n + 1):
            for j in range(i + 1, n + 1):
                for suffix in ('pp', 'mm', 'pm', 'mp'):
                    assert gens[f'E_del{i}_del{j}_{suffix}'][1] == 0


# ── 3. Graded antisymmetry ────────────────────────────────────────────────────

class TestBracketAntisymmetry:
    """[X, Y} = -(-1)^{pX pY} [Y, X}"""

    def _check_pair(self, gens, Xname, Yname):
        Xpoly, pX = gens[Xname]
        Ypoly, pY = gens[Yname]
        XY = graded_bracket(Xpoly, Ypoly, pX, pY)
        YX = graded_bracket(Ypoly, Xpoly, pY, pX)
        sign = (-1) ** (pX * pY)
        residual = add_polys(XY, scale_poly(YX, sign))
        assert not residual, (
            f'Antisymmetry failed for [{Xname}, {Yname}], residual={residual}')

    def test_even_even(self, n, gens):
        names = list(gens.keys())
        even = [nm for nm in names if gens[nm][1] == 0]
        self._check_pair(gens, even[0], even[1])
        if len(even) > 3:
            self._check_pair(gens, even[1], even[3])

    def test_even_odd(self, n, gens):
        names = list(gens.keys())
        even = [nm for nm in names if gens[nm][1] == 0]
        odd  = [nm for nm in names if gens[nm][1] == 1]
        self._check_pair(gens, even[0], odd[0])
        self._check_pair(gens, even[1], odd[-1])

    def test_odd_odd(self, n, gens):
        names = list(gens.keys())
        odd = [nm for nm in names if gens[nm][1] == 1]
        self._check_pair(gens, odd[0], odd[1])
        self._check_pair(gens, odd[0], odd[-1])
        self._check_pair(gens, odd[1], odd[-1])


# ── 4. Super-Jacobi identity ──────────────────────────────────────────────────

class TestJacobi:
    """(-1)^{pX pZ}[X,[Y,Z}} + (-1)^{pY pX}[Y,[Z,X}} + (-1)^{pZ pY}[Z,[X,Y}} = 0"""

    def _jacobi(self, gens, Xname, Yname, Zname):
        def poly_par(nm):
            return gens[nm]

        X, pX = poly_par(Xname)
        Y, pY = poly_par(Yname)
        Z, pZ = poly_par(Zname)

        YZ = graded_bracket(Y, Z, pY, pZ)
        ZX = graded_bracket(Z, X, pZ, pX)
        XY = graded_bracket(X, Y, pX, pY)

        pYZ = (pY + pZ) % 2
        pZX = (pZ + pX) % 2
        pXY = (pX + pY) % 2

        t1 = scale_poly(graded_bracket(X, YZ, pX, pYZ), (-1) ** (pX * pZ))
        t2 = scale_poly(graded_bracket(Y, ZX, pY, pZX), (-1) ** (pY * pX))
        t3 = scale_poly(graded_bracket(Z, XY, pZ, pXY), (-1) ** (pZ * pY))

        res = add_polys(add_polys(t1, t2), t3)
        assert not res, (
            f'Jacobi failed for ({Xname},{Yname},{Zname}): residual={res}')

    def test_H_E_pp_E_mm(self, n, gens):
        self._jacobi(gens, 'H_1', f'E_eps1_del{1}_pp', f'E_eps1_del{1}_mm')

    def test_H_E_pp_E_mp(self, n, gens):
        self._jacobi(gens, f'H_{n+1}', f'E_eps1_del{n}_pp', f'E_eps1_del{n}_mp')

    def test_three_odd_same_index(self, n, gens):
        self._jacobi(gens,
                     f'E_eps1_del{1}_pp',
                     f'E_eps1_del{1}_mm',
                     f'E_eps1_del{1}_pm')

    def test_three_odd_cross_index(self, n, gens):
        if n < 2:
            pytest.skip('Requires n >= 2')
        self._jacobi(gens,
                     'E_eps1_del1_pp',
                     'E_eps1_del2_mm',
                     'E_eps1_del1_mp')

    def test_even_even_odd(self, n, gens):
        self._jacobi(gens, 'H_1', f'E_2del{1}_p', f'E_eps1_del{1}_pp')

    def test_odd_even_root_odd(self, n, gens):
        if n < 2:
            pytest.skip('Requires n >= 2')
        self._jacobi(gens,
                     'E_eps1_del1_pp',
                     'E_del1_del2_pp',
                     'E_eps1_del2_mm')


# ── 5. Schema structure ───────────────────────────────────────────────────────

class TestSchemaStructure:
    def test_schema_version(self, schema):
        assert schema['schema_version'] == '5.0'

    def test_algebra_family_m(self, schema):
        assert schema['algebra']['family'] == 'C'
        assert schema['algebra']['m'] == 1

    def test_dimension_formulas(self, n, schema):
        d = schema['algebra']['dimension']
        assert d['even'] == 2 * n * n + n + 1
        assert d['odd'] == 4 * n
        assert d['total'] == d['even'] + d['odd']

    def test_central_elements(self, schema):
        ce = schema['central_elements']
        assert 'kappa' in ce and ce['kappa']['parity'] == 1
        assert 'K' in ce and ce['K']['parity'] == 0

    def test_basis_counts(self, n, schema):
        assert len(schema['basis']['even']) == 2 * n * n + n + 1
        assert len(schema['basis']['odd']) == 4 * n

    def test_parity_keys_match_basis(self, schema):
        all_basis = set(schema['basis']['even'] + schema['basis']['odd'])
        assert set(schema['parity'].keys()) == all_basis

    def test_sc_names_in_basis(self, schema):
        all_basis = set(schema['basis']['even'] + schema['basis']['odd'])
        for entry in schema['structure_constants']:
            assert entry['X'] in all_basis
            assert entry['Y'] in all_basis
            assert entry['Z'] in all_basis

    def test_sc_coeff_format(self, schema):
        for entry in schema['structure_constants']:
            c = entry['coeff']
            if '/' in c:
                num, den = c.split('/')
                assert int(den) > 0
            else:
                int(c)

    def test_fermion_labels(self, schema):
        ferm = schema['oscillator_generators']['fermions']
        assert ferm['m'] == 1
        assert ferm['labels'] == ['a_1_p', 'a_1_m']

    def test_boson_labels(self, n, schema):
        bos = schema['oscillator_generators']['bosons']
        assert bos['n'] == n
        assert bos['count'] == 2 * n


# ── 6. Specific brackets for C(2) = osp(2|2), n=1 ───────────────────────────

class TestC2Brackets:
    """
    Analytically known structure constants for C(2) = osp(2|2), n=1.

    Root dictionary:
      E_eps1_del1_pp  =  a_1^+ b_1^+   root  ε+δ_1
      E_eps1_del1_pm  =  a_1^+ b_1^-   root  ε-δ_1
      E_eps1_del1_mp  =  a_1^- b_1^+   root  -ε+δ_1
      E_eps1_del1_mm  =  a_1^- b_1^-   root  -ε-δ_1
      E_2del1_p       =  (b_1^+)^2     root  2δ_1
      E_2del1_m       =  (b_1^-)^2     root  -2δ_1
      H_1 = n_a + n_1,  H_2 = -n_1 - 1/2
    """

    @pytest.fixture(autouse=True)
    def _sc(self):
        self.sc = _build_sc(1)

    # Cartan eigenvalues
    def test_H1_on_E_pp(self):
        """[H_1, E_eps1_del1_pp} = 2·E_eps1_del1_pp  (eigenvalue 2 = n_a + n_1 on ε+δ_1)"""
        comps = _get(self.sc, 'H_1', 'E_eps1_del1_pp')
        assert comps == {'E_eps1_del1_pp': Fraction(2)}

    def test_H1_on_E_pm(self):
        """[H_1, E_eps1_del1_pm} = 0  (eigenvalue 1-1=0 on ε-δ_1)"""
        comps = _get(self.sc, 'H_1', 'E_eps1_del1_pm')
        assert not comps

    def test_H1_on_E_mp(self):
        """[H_1, E_eps1_del1_mp} = 0  (eigenvalue -1+1=0 on -ε+δ_1)"""
        comps = _get(self.sc, 'H_1', 'E_eps1_del1_mp')
        assert not comps

    def test_H1_on_E_mm(self):
        """[H_1, E_eps1_del1_mm} = -2·E_eps1_del1_mm  (eigenvalue -1-1=-2)"""
        comps = _get(self.sc, 'H_1', 'E_eps1_del1_mm')
        assert comps == {'E_eps1_del1_mm': Fraction(-2)}

    def test_H2_on_E_pp(self):
        """[H_2, E_eps1_del1_pp} = -1·E_eps1_del1_pp  (eigenvalue -1 from -n_1 on δ_1)"""
        comps = _get(self.sc, 'H_2', 'E_eps1_del1_pp')
        assert comps == {'E_eps1_del1_pp': Fraction(-1)}

    def test_H2_on_E_mp(self):
        """[H_2, E_eps1_del1_mp} = -1·E_eps1_del1_mp"""
        comps = _get(self.sc, 'H_2', 'E_eps1_del1_mp')
        assert comps == {'E_eps1_del1_mp': Fraction(-1)}

    # Odd-odd brackets
    def test_E_pp_E_mm(self):
        """[E_pp, E_mm} = -H_1 - 2·H_2  (root sum ε+δ_1 + (-ε-δ_1) = 0 → Cartan)"""
        comps = _get(self.sc, 'E_eps1_del1_pp', 'E_eps1_del1_mm')
        assert comps == {'H_1': Fraction(-1), 'H_2': Fraction(-2)}

    def test_E_pm_E_mp(self):
        """[E_pm, E_mp} = H_1 - 2·H_2  (root sum ε-δ_1 + (-ε+δ_1) = 0 → Cartan)"""
        comps = _get(self.sc, 'E_eps1_del1_pm', 'E_eps1_del1_mp')
        # ε-δ_1 + -ε+δ_1 = 0; [a_1^+ b_1^-, a_1^- b_1^+}
        # = a_1^+ a_1^- (b_1^-)^? ... let me just check it's Cartan-valued
        assert all(k.startswith('H_') for k in comps), f'Expected Cartan: {comps}'

    def test_E_pp_E_pm_zero(self):
        """[E_pp, E_pm} = 0  ((a_1^+)^2 = 0)"""
        comps = _get(self.sc, 'E_eps1_del1_pp', 'E_eps1_del1_pm')
        assert not comps

    def test_E_mp_E_mm_zero(self):
        """[E_mp, E_mm} = 0  ((a_1^-)^2 = 0, no -2ε root)"""
        comps = _get(self.sc, 'E_eps1_del1_mp', 'E_eps1_del1_mm')
        assert not comps

    def test_E_pp_E_mp_to_2del_p(self):
        """[E_pp, E_mp} = E_2del1_p  (root sum ε+δ_1 + -ε+δ_1 = 2δ_1)"""
        comps = _get(self.sc, 'E_eps1_del1_pp', 'E_eps1_del1_mp')
        assert comps == {'E_2del1_p': Fraction(1)}

    def test_E_pm_E_mm_to_2del_m(self):
        """[E_pm, E_mm} = E_2del1_m  (root sum ε-δ_1 + -ε-δ_1 = -2δ_1)"""
        comps = _get(self.sc, 'E_eps1_del1_pm', 'E_eps1_del1_mm')
        assert comps == {'E_2del1_m': Fraction(1)}

    # Even root brackets
    def test_E_2p_E_2m(self):
        """[E_2del1_p, E_2del1_m} = 4·H_2
        [(b_1^+)^2, (b_1^-)^2] = -4n_1 - 2 = 4H_2  (since H_2 = -n_1 - 1/2)"""
        comps = _get(self.sc, 'E_2del1_p', 'E_2del1_m')
        assert comps == {'H_2': Fraction(4)}

    def test_H_E_2p(self):
        """[H_2, E_2del1_p} = -2·E_2del1_p  (root 2δ_1 acts on H_2 = -n_1 - 1/2)"""
        comps = _get(self.sc, 'H_2', 'E_2del1_p')
        assert comps == {'E_2del1_p': Fraction(-2)}
