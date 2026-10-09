"""Tests for C(n+1) structure constant generator."""

import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from C_generators import CnAlgebra, build_algebra, build_schema1_json

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')


class TestDimensions:
    """Test generator counts match dimension formulas."""

    def test_n1_even_dim(self):
        alg = CnAlgebra(1)
        gens, pars, _ = alg.build_generators()
        even = [l for l, p in pars.items() if p == 0]
        assert len(even) == 4, f"C(2) even dim should be 4, got {len(even)}"

    def test_n1_odd_dim(self):
        alg = CnAlgebra(1)
        gens, pars, _ = alg.build_generators()
        odd = [l for l, p in pars.items() if p == 1]
        assert len(odd) == 4, f"C(2) odd dim should be 4, got {len(odd)}"

    def test_n2_even_dim(self):
        alg = CnAlgebra(2)
        gens, pars, _ = alg.build_generators()
        even = [l for l, p in pars.items() if p == 0]
        assert len(even) == 11, f"C(3) even dim should be 11, got {len(even)}"

    def test_n2_odd_dim(self):
        alg = CnAlgebra(2)
        gens, pars, _ = alg.build_generators()
        odd = [l for l, p in pars.items() if p == 1]
        assert len(odd) == 8, f"C(3) odd dim should be 8, got {len(odd)}"

    def test_n3_even_dim(self):
        alg = CnAlgebra(3)
        gens, pars, _ = alg.build_generators()
        even = [l for l, p in pars.items() if p == 0]
        assert len(even) == 22, f"C(4) even dim should be 22, got {len(even)}"

    def test_n3_odd_dim(self):
        alg = CnAlgebra(3)
        gens, pars, _ = alg.build_generators()
        odd = [l for l, p in pars.items() if p == 1]
        assert len(odd) == 12, f"C(4) odd dim should be 12, got {len(odd)}"


class TestFermionicAlgebra:
    """Test basic fermionic operator relations."""

    def test_a1p_squared_is_zero(self):
        alg = CnAlgebra(1)
        a1p = {alg.make_mon(a1p=1): Fraction(1)}
        result = alg.multiply(a1p, a1p)
        assert result == {}, f"(a1+)^2 should be 0, got {result}"

    def test_a1m_squared_is_zero(self):
        alg = CnAlgebra(1)
        a1m = {alg.make_mon(a1m=1): Fraction(1)}
        result = alg.multiply(a1m, a1m)
        assert result == {}, f"(a1-)^2 should be 0, got {result}"

    def test_anticommutator_is_1(self):
        alg = CnAlgebra(1)
        a1p = {alg.make_mon(a1p=1): Fraction(1)}
        a1m = {alg.make_mon(a1m=1): Fraction(1)}
        # {a1-, a1+} = a1-*a1+ + a1+*a1- should = 1
        prod1 = alg.multiply(a1m, a1p)
        prod2 = alg.multiply(a1p, a1m)
        combined = dict(prod1)
        for m, c in prod2.items():
            combined[m] = combined.get(m, Fraction(0)) + c
        combined = {k: v for k, v in combined.items() if v != 0}
        zero_mon = alg._zero
        assert combined == {zero_mon: Fraction(1)}, \
            f"{{a1-,a1+}} should be 1, got {combined}"


class TestBosonicAlgebra:
    """Test basic bosonic operator relations."""

    def test_bos_commutator(self):
        alg = CnAlgebra(1)
        b1m = {alg.make_mon(b1m=1): Fraction(1)}
        b1p = {alg.make_mon(b1p=1): Fraction(1)}
        # [b1-, b1+] = b1-*b1+ - b1+*b1- = 1
        prod_mp = alg.multiply(b1m, b1p)
        prod_pm = alg.multiply(b1p, b1m)
        diff = dict(prod_mp)
        for m, c in prod_pm.items():
            diff[m] = diff.get(m, Fraction(0)) - c
        diff = {k: v for k, v in diff.items() if v != 0}
        zero_mon = alg._zero
        assert diff == {zero_mon: Fraction(1)}, \
            f"[b1-,b1+] should be 1, got {diff}"


class TestStructureConstants:
    """Test specific known structure constants."""

    def test_cartan_root_bracket_H1_E_eps1_del1_pp(self):
        """[H_1, E_{eps+del1}] should equal 2*E_{eps+del1}.

        H_1 = N^f + N_1; a_1^+ contributes weight +1 and b_1^+ contributes +1,
        giving total weight 2 for the root eps+del_1 under H_1.
        """
        alg = CnAlgebra(1)
        gens, pars, basis_order = alg.build_generators()
        H1 = gens['H_1']
        E = gens['E_eps1_del1_pp']
        bracket = alg.super_comm(H1, 0, E, 1)
        decomp = alg.decompose(bracket, gens, pars, basis_order)
        assert decomp == {'E_eps1_del1_pp': Fraction(2)}, \
            f"[H_1, E_eps1_del1_pp] should be 2*E_eps1_del1_pp, got {decomp}"

    def test_anticommutator_odd_odd_gives_cartan(self):
        """[E_{eps+del1}, E_{-eps-del1}] should be a Cartan element."""
        alg = CnAlgebra(1)
        gens, pars, basis_order = alg.build_generators()
        E_pp = gens['E_eps1_del1_pp']
        E_mm = gens['E_eps1_del1_mm']
        bracket = alg.super_comm(E_pp, 1, E_mm, 1)
        decomp = alg.decompose(bracket, gens, pars, basis_order)
        # All results should be Cartan elements
        for label in decomp:
            assert label.startswith('H_'), \
                f"[E_pp, E_mm] should be Cartan, but got {label}"

    def test_cartan_cartan_commute(self):
        """[H_j, H_k] = 0 for all j, k."""
        alg = CnAlgebra(2)
        gens, pars, basis_order = alg.build_generators()
        cartan = [l for l in basis_order if l.startswith('H_')]
        for h1 in cartan:
            for h2 in cartan:
                bracket = alg.super_comm(gens[h1], 0, gens[h2], 0)
                assert bracket == {}, f"[{h1}, {h2}] should be 0, got {bracket}"


class TestSchemaJSON:
    """Test the generated JSON files."""

    def _load(self, n):
        path = os.path.join(DATA_DIR, f'C_{n}_structure.json')
        with open(path) as f:
            return json.load(f)

    def test_schema_version(self):
        for n in [1, 2, 3]:
            data = self._load(n)
            assert data['schema_version'] == '5.0'

    def test_algebra_family(self):
        for n in [1, 2, 3]:
            data = self._load(n)
            assert data['algebra']['family'] == 'C'
            assert data['algebra']['m'] == 1
            assert data['algebra']['n'] == n

    def test_dimensions(self):
        expected = {1: (4, 4, 8), 2: (11, 8, 19), 3: (22, 12, 34)}
        for n, (even, odd, total) in expected.items():
            data = self._load(n)
            assert data['algebra']['dimension']['even'] == even
            assert data['algebra']['dimension']['odd'] == odd
            assert data['algebra']['dimension']['total'] == total

    def test_central_elements_are_top_level(self):
        for n in [1, 2, 3]:
            data = self._load(n)
            assert 'central_elements' in data
            assert 'kappa' in data['central_elements']
            assert 'K' in data['central_elements']
            assert data['central_elements']['kappa']['parity'] == 1
            assert data['central_elements']['K']['parity'] == 0

    def test_basis_parity_consistency(self):
        for n in [1, 2, 3]:
            data = self._load(n)
            parity = data['parity']
            for label in data['basis']['even']:
                assert parity[label] == 0, f"n={n}: {label} should be even"
            for label in data['basis']['odd']:
                assert parity[label] == 1, f"n={n}: {label} should be odd"

    def test_structure_constant_generator_in_basis(self):
        for n in [1, 2, 3]:
            data = self._load(n)
            all_labels = set(data['basis']['even'] + data['basis']['odd'])
            for sc in data['structure_constants']:
                assert sc['X'] in all_labels, f"n={n}: X={sc['X']} not in basis"
                assert sc['Y'] in all_labels, f"n={n}: Y={sc['Y']} not in basis"
                assert sc['Z'] in all_labels, f"n={n}: Z={sc['Z']} not in basis"
