from fractions import Fraction

import pytest

from verify_C_structure import check_antisymmetry, check_jacobi, load_structure, verify


@pytest.mark.parametrize("n", [1, 2, 3])
def test_structure_passes(n):
    r = verify(n)
    assert r["triples"] == r["dim"] ** 3
    assert r["parity_failures"] == r["antisymmetry_failures"] == r["jacobi_failures"] == 0


def test_checker_detects_corruption():
    basis, par, sc = load_structure(1)
    key = ("E_2del1_p", "E_2del1_m")
    sc[key] = {"H_2": Fraction(2)}  # corrupt one entry
    assert check_antisymmetry(basis, par, sc)
    assert check_jacobi(basis, par, sc)[0]
