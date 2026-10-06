import json
import os
from fractions import Fraction

import pytest

from C_coboundary import (apply_coboundary, build_schema4, check_layer1_consistency,
                          general_coboundary, odd_map_unknowns, reference_f)
from C_generators import DATA_DIR
from verify_C_structure import load_structure


@pytest.mark.parametrize("n", [1, 2, 3])
def test_unknown_count(n):
    basis, par, _ = load_structure(n)
    e, o = 2 * n * n + n + 1, 4 * n
    assert len(odd_map_unknowns(basis, par)) == 2 * e * o
    assert len(odd_map_unknowns(basis, par, True)) == 2 * e * o + o


@pytest.mark.parametrize("n", [1, 2])
def test_inner_odd_derivation_is_cocycle(n):
    """f = ad(xi) for odd xi must have delta f = 0 (checks the sign convention)."""
    basis, par, sc = load_structure(n)
    delta = general_coboundary(basis, par, sc)
    for xi in [b for b in basis if par[b] == 1]:
        fmap = {Y: {Z: {"t": c} for Z, c in sc.get((xi, Y), {}).items()} for Y in basis}
        assert apply_coboundary(delta, fmap) == {}


@pytest.mark.parametrize("n", [1, 2, 3])
def test_json_layer1_consistency(n):
    with open(os.path.join(DATA_DIR, f"C_{n}_coboundary.json")) as f:
        d4 = json.load(f)
    assert d4["layer"] == 4
    assert check_layer1_consistency(n, d4) == 0


def test_json_matches_generator():
    with open(os.path.join(DATA_DIR, "C_1_coboundary.json")) as f:
        d4 = json.load(f)
    fresh = build_schema4(1)
    assert d4["reference_map"] == fresh["reference_map"]
    assert d4["general_coboundary"] == fresh["general_coboundary"]


def test_reference_f_is_odd():
    basis, par, _ = load_structure(2)
    P = dict(par, K=0)
    for X, r in reference_f(2).items():
        for Z in r:
            assert P[Z] != par[X]
