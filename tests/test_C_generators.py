"""Tests for C(n+1) = osp(2|2n) structure constant generator."""

import json
import sys
import os
import pytest
from fractions import Fraction

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from C_generators import CnAlgebra


@pytest.mark.parametrize("n,expected_even,expected_odd,expected_total", [
    (1, 4, 4, 8),
    (2, 11, 8, 19),
    (3, 22, 12, 34),
])
def test_generator_counts(n, expected_even, expected_odd, expected_total):
    alg = CnAlgebra(n)
    assert len(alg.even_basis) == expected_even
    assert len(alg.odd_basis) == expected_odd
    assert len(alg.all_basis) == expected_total


@pytest.mark.parametrize("n", [1, 2, 3])
def test_parity_assignment(n):
    alg = CnAlgebra(n)
    for name in alg.even_basis:
        assert alg.gen_parity[name] == 0, f"{name} should be even"
    for name in alg.odd_basis:
        assert alg.gen_parity[name] == 1, f"{name} should be odd"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_dimension_formula(n):
    alg = CnAlgebra(n)
    assert len(alg.even_basis) == 2 * n * n + n + 1
    assert len(alg.odd_basis) == 4 * n


def test_specific_bracket_n1():
    """Test [E_eps1_del1_pp, E_eps1_del1_mp] = E_2del1_p for n=1."""
    alg = CnAlgebra(1)
    result = alg.compute_bracket('E_eps1_del1_pp', 'E_eps1_del1_mp')
    assert result == {'E_2del1_p': Fraction(1)}


def test_specific_bracket_cartan_n1():
    """Test {E_eps1_del1_pp, E_eps1_del1_mm} = -H_1 - 2*H_2 for n=1."""
    alg = CnAlgebra(1)
    result = alg.compute_bracket('E_eps1_del1_pp', 'E_eps1_del1_mm')
    assert result == {'H_1': Fraction(-1), 'H_2': Fraction(-2)}


def test_cartan_eigenvalue_n1():
    """Test [H_1, E_eps1_del1_pp] = 2 * E_eps1_del1_pp."""
    alg = CnAlgebra(1)
    result = alg.compute_bracket('H_1', 'E_eps1_del1_pp')
    assert result == {'E_eps1_del1_pp': Fraction(2)}


def test_cartan_eigenvalue_E2del_n1():
    """Test [H_1, E_2del1_p] = 2 * E_2del1_p."""
    alg = CnAlgebra(1)
    result = alg.compute_bracket('H_1', 'E_2del1_p')
    assert result == {'E_2del1_p': Fraction(2)}


@pytest.mark.parametrize("n", [1, 2, 3])
def test_json_output_exists(n):
    filepath = f'data/C_{n}_structure.json'
    assert os.path.exists(filepath), f"{filepath} not found"
    with open(filepath) as f:
        data = json.load(f)
    assert data['schema_version'] == '5.0'
    assert data['algebra']['family'] == 'C'
    assert data['algebra']['n'] == n
    assert data['algebra']['m'] == 1


@pytest.mark.parametrize("n", [1, 2, 3])
def test_json_dimensions(n):
    with open(f'data/C_{n}_structure.json') as f:
        data = json.load(f)
    dim = data['algebra']['dimension']
    assert dim['even'] == 2 * n * n + n + 1
    assert dim['odd'] == 4 * n
    assert dim['total'] == dim['even'] + dim['odd']


@pytest.mark.parametrize("n", [1, 2, 3])
def test_json_basis_counts(n):
    with open(f'data/C_{n}_structure.json') as f:
        data = json.load(f)
    assert len(data['basis']['even']) == 2 * n * n + n + 1
    assert len(data['basis']['odd']) == 4 * n


@pytest.mark.parametrize("n", [1, 2, 3])
def test_central_elements(n):
    with open(f'data/C_{n}_structure.json') as f:
        data = json.load(f)
    assert 'K' in data['central_elements']
    assert 'kappa' in data['central_elements']
    assert data['central_elements']['K']['parity'] == 0
    assert data['central_elements']['kappa']['parity'] == 1
