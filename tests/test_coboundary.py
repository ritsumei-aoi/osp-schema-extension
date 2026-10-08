"""Tests for the coboundary computation (src/C_coboundary.py)."""

import os
import sys
from fractions import Fraction

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'src'))

import C_coboundary as cb  # noqa: E402
from verify_C_structure import load_structure  # noqa: E402


def _setup(n):
    _doc, basis, parity_map, table = load_structure(n, cb.DATA_DIR)
    parity = {x: parity_map[x] for x in basis}
    return basis, parity, table


@pytest.mark.parametrize('n', (1, 2))
def test_every_elementary_coboundary_passes_checks(n):
    basis, parity, table = _setup(n)
    for (i, j) in cb.elementary_maps(basis, parity):
        delta = cb.delta_of_elementary(basis, parity, table, i, j)
        fails = cb.check_map(basis, parity, table, delta)
        assert fails == {'antisymmetry': 0, 'parity': 0, 'cocycle': 0}, (i, j)


def test_sign_flip_in_coboundary_is_detected():
    # Negative control: flipping the sign of the f([X,Y]) term must break the checks,
    # otherwise the checks would not be testing the coboundary formula.
    basis, parity, table = _setup(1)
    i, j = next((i, j) for (i, j) in cb.elementary_maps(basis, parity))
    delta = cb.delta_of_elementary(basis, parity, table, i, j)
    f = {j: {i: Fraction(1)}}
    flipped = {key: dict(img) for key, img in delta.items()}
    for x in basis:
        for y in basis:
            bxy = cb._bracket(table, {x: Fraction(1)}, {y: Fraction(1)})
            extra = {}
            for z, c in bxy.items():
                for w, d in f.get(z, {}).items():
                    extra[w] = extra.get(w, 0) + 2 * c * d
            if extra:
                updated = cb._add(flipped.get((x, y), {}), extra)
                if updated:
                    flipped[(x, y)] = updated
                else:
                    flipped.pop((x, y), None)
    fails = cb.check_map(basis, parity, table, flipped)
    assert fails['cocycle'] > 0 or fails['antisymmetry'] > 0
