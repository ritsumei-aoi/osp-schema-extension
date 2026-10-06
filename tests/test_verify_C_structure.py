"""Tests for the I04 verifier: real data passes, corrupted data is detected."""
import copy

import pytest

from verify_C_structure import load_structure, check_antisymmetry, check_jacobi, verify


@pytest.mark.parametrize("n", (1, 2, 3))
def test_structure_passes(n):
    r = verify(n)
    assert r["triples"] == r["dim"] ** 3
    assert r["antisymmetry_failures"] == []
    assert r["jacobi_failures"] == []


def test_verifier_detects_corruption():
    basis, par, sc = load_structure(1)
    bad = copy.deepcopy(sc)
    bad[("E_2del1_p", "E_2del1_m")]["H_2"] += 1          # break one constant ...
    assert check_antisymmetry(basis, par, bad)
    bad[("E_2del1_m", "E_2del1_p")]["H_2"] -= 1          # ... keep antisymmetry consistent
    assert not check_antisymmetry(basis, par, bad)
    _, fails = check_jacobi(basis, par, bad)
    assert fails
