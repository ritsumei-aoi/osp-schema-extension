"""Tests for C(n+1) structure constants (Schema 1)."""

import json
import os
import sys
import pytest
from fractions import Fraction

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from C_generators import build_basis, build_parity, gen_realization, build_schema1, osc_order


DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')


def load_schema(n):
    path = os.path.join(DATA_DIR, f'C_{n}_structure.json')
    with open(path) as f:
        return json.load(f)


@pytest.mark.parametrize("n,expected_odd,expected_even", [
    (1, 4, 4),
    (2, 8, 11),
    (3, 12, 22),
])
def test_basis_counts(n, expected_odd, expected_even):
    schema = load_schema(n)
    assert len(schema['basis']['odd']) == expected_odd
    assert len(schema['basis']['even']) == expected_even
    assert schema['algebra']['dimension']['odd'] == expected_odd
    assert schema['algebra']['dimension']['even'] == expected_even
    assert schema['algebra']['dimension']['total'] == expected_odd + expected_even


@pytest.mark.parametrize("n", [1, 2, 3])
def test_parity_values(n):
    schema = load_schema(n)
    parity = schema['parity']
    odd_basis = schema['basis']['odd']
    even_basis = schema['basis']['even']
    for g in odd_basis:
        assert parity[g] == 1, f"{g} should be odd"
    for g in even_basis:
        assert parity[g] == 0, f"{g} should be even"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema_version(n):
    schema = load_schema(n)
    assert schema['schema_version'] == '5.0'
    assert schema['algebra']['family'] == 'C'
    assert schema['algebra']['m'] == 1
    assert schema['algebra']['n'] == n


@pytest.mark.parametrize("n", [1, 2, 3])
def test_central_elements(n):
    schema = load_schema(n)
    ce = schema['central_elements']
    assert 'K' in ce and ce['K']['parity'] == 0
    assert 'kappa' in ce and ce['kappa']['parity'] == 1
    assert ce['kappa']['nilpotent'] is True


@pytest.mark.parametrize("n", [1, 2, 3])
def test_structure_constants_parity_conservation(n):
    """[X, Y} must have parity p(X)+p(Y) mod 2."""
    schema = load_schema(n)
    parity = schema['parity']
    parity['K'] = 0
    for sc in schema['structure_constants']:
        X, Y, Z = sc['X'], sc['Y'], sc['Z']
        pX = parity[X]
        pY = parity[Y]
        pZ = parity[Z]
        assert (pX + pY) % 2 == pZ, f"Parity not conserved: [{X},{Y}]={Z}: {pX}+{pY}!={pZ}"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_generator_count_eps1(n):
    """Should have 4n odd generators labeled E_eps1_..."""
    schema = load_schema(n)
    eps_gens = [g for g in schema['basis']['odd'] if 'eps1' in g]
    assert len(eps_gens) == 4 * n


@pytest.mark.parametrize("n", [1, 2, 3])
def test_cartan_count(n):
    """Should have n+1 Cartan generators H_1,...,H_{n+1}."""
    schema = load_schema(n)
    cartans = [g for g in schema['basis']['even'] if g.startswith('H_')]
    assert len(cartans) == n + 1


@pytest.mark.parametrize("n", [1, 2, 3])
def test_structure_constants_nonempty(n):
    schema = load_schema(n)
    assert len(schema['structure_constants']) > 0
