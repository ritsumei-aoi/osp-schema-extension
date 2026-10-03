"""Unit tests for C(n+1) structure constants."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import json
import pytest
from fractions import Fraction
from C_generators import CnPlusOne, generate_and_save


# -----------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------

def load_sc(n):
    path = os.path.join(os.path.dirname(__file__), '..', 'data', f'C_{n}_structure.json')
    with open(path) as f:
        return json.load(f)


def get_bracket_map(sc_list):
    """Convert structure constant list to {(X,Y,Z): coeff}."""
    m = {}
    for e in sc_list:
        key = (e['X'], e['Y'], e['Z'])
        m[key] = Fraction(e['coeff'])
    return m


def bracket_result(sc_map, gx, gy):
    """Return {Z: coeff} for [X, Y] from sc_map."""
    res = {}
    for (X, Y, Z), c in sc_map.items():
        if X == gx and Y == gy:
            res[Z] = res.get(Z, Fraction(0)) + c
    return {Z: c for Z, c in res.items() if c}


# -----------------------------------------------------------------------
# Parity tests
# -----------------------------------------------------------------------

@pytest.mark.parametrize("n", [1, 2, 3])
def test_generator_counts(n):
    """Verify generator counts match dimension formula."""
    alg = CnPlusOne(n)
    even_gens = [g for g in alg.generators if alg.gen_parity[g] == 0]
    odd_gens  = [g for g in alg.generators if alg.gen_parity[g] == 1]
    assert len(even_gens) == 2*n*n + n + 1, f"Even dim mismatch for n={n}"
    assert len(odd_gens)  == 4*n,           f"Odd dim mismatch for n={n}"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_parity_of_brackets(n):
    """Bracket of generators X, Y must have parity p(X)+p(Y) mod 2."""
    alg = CnPlusOne(n)
    sc_list = alg.compute_structure_constants()
    for entry in sc_list:
        px = alg.gen_parity[entry['X']]
        py = alg.gen_parity[entry['Y']]
        pz = alg.gen_parity[entry['Z']]
        assert (px + py) % 2 == pz, (
            f"Parity failure: [{entry['X']},{entry['Y']}] -> {entry['Z']}: "
            f"p(X)+p(Y)={(px+py)%2}, p(Z)={pz}"
        )


# -----------------------------------------------------------------------
# Specific bracket checks for n=1
# -----------------------------------------------------------------------

def test_n1_h1_on_e2del1_p():
    alg = CnPlusOne(1)
    br = alg.bracket('H_1', 'E_2del1_p')
    gens = alg.element_to_gens(br)
    assert gens == {'E_2del1_p': Fraction(2)}, f"Got {gens}"


def test_n1_h2_on_e2del1_p():
    alg = CnPlusOne(1)
    br = alg.bracket('H_2', 'E_2del1_p')
    gens = alg.element_to_gens(br)
    assert gens == {'E_2del1_p': Fraction(-2)}, f"Got {gens}"


def test_n1_e2del1p_e2del1m():
    """[E_2del1_p, E_2del1_m] = 4 * H_2."""
    alg = CnPlusOne(1)
    br = alg.bracket('E_2del1_p', 'E_2del1_m')
    gens = alg.element_to_gens(br)
    assert gens == {'H_2': Fraction(4)}, f"Got {gens}"


def test_n1_odd_bracket_pp_mp():
    """{E_eps1_del1_pp, E_eps1_del1_mp} = E_2del1_p."""
    alg = CnPlusOne(1)
    br = alg.bracket('E_eps1_del1_pp', 'E_eps1_del1_mp')
    gens = alg.element_to_gens(br)
    assert gens == {'E_2del1_p': Fraction(1)}, f"Got {gens}"


def test_n1_odd_bracket_pp_mm():
    """{E_eps1_del1_pp, E_eps1_del1_mm} = -H_1 - 2*H_2."""
    alg = CnPlusOne(1)
    br = alg.bracket('E_eps1_del1_pp', 'E_eps1_del1_mm')
    gens = alg.element_to_gens(br)
    assert gens == {'H_1': Fraction(-1), 'H_2': Fraction(-2)}, f"Got {gens}"


def test_n1_odd_bracket_pm_mp():
    """{E_eps1_del1_pm, E_eps1_del1_mp} = H_1."""
    alg = CnPlusOne(1)
    br = alg.bracket('E_eps1_del1_pm', 'E_eps1_del1_mp')
    gens = alg.element_to_gens(br)
    assert gens == {'H_1': Fraction(1)}, f"Got {gens}"


def test_n1_h1_zero_bracket():
    """[H_1, E_eps1_del1_pm] = 0 (weight 0 under H_1)."""
    alg = CnPlusOne(1)
    br = alg.bracket('H_1', 'E_eps1_del1_pm')
    gens = alg.element_to_gens(br)
    assert gens == {}, f"Expected 0, got {gens}"


# -----------------------------------------------------------------------
# JSON file existence and schema structure
# -----------------------------------------------------------------------

@pytest.mark.parametrize("n", [1, 2, 3])
def test_json_schema_keys(n):
    """Verify all required top-level keys are present in the JSON."""
    doc = load_sc(n)
    required = {'schema_version', 'algebra', 'oscillator_generators',
                'oscillator_relations', 'central_elements', 'basis',
                'parity', 'generator_realization', 'structure_constants', 'metadata'}
    assert required <= set(doc.keys()), f"Missing keys: {required - set(doc.keys())}"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_json_algebra_fields(n):
    """Verify mandatory algebra fields."""
    doc = load_sc(n)
    alg = doc['algebra']
    assert alg['family'] == 'C'
    assert alg['m'] == 1
    assert alg['n'] == n
    assert alg['dimension']['even'] == 2*n*n + n + 1
    assert alg['dimension']['odd'] == 4*n


@pytest.mark.parametrize("n", [1, 2, 3])
def test_json_central_elements(n):
    """Verify central_elements key is top-level and contains K and kappa."""
    doc = load_sc(n)
    ce = doc['central_elements']
    assert 'K' in ce and 'kappa' in ce
    assert ce['K']['parity'] == 0
    assert ce['kappa']['parity'] == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
