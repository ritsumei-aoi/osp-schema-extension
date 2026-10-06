from fractions import Fraction

import pytest

from verify_C_structure import (check_antisymmetry, check_jacobi, check_parity, load_structure,
                                verify)


@pytest.mark.parametrize("n", [1, 2, 3])
def test_all_checks_pass(n):
    assert verify(n, verbose=False)


def test_corruption_detected():
    _, basis, parity, sc = load_structure(1)
    # Perturb one constant symmetrically (antisymmetry still holds) -> Jacobi must fail.
    x, y = "E_2del1_p", "E_2del1_m"
    sc[(x, y)] = {"H_2": Fraction(3)}
    sc[(y, x)] = {"H_2": Fraction(-3)}
    assert not check_antisymmetry(basis, parity, sc)
    assert not check_parity(parity, sc)
    fails, _ = check_jacobi(basis, parity, sc)
    assert fails
    # Break antisymmetry.
    sc[(y, x)] = {"H_2": Fraction(3)}
    assert check_antisymmetry(basis, parity, sc)
