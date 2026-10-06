import os
import sys
from fractions import Fraction

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from verify_C_structure import (bracket_table, check_antisymmetry, check_jacobi,  # noqa: E402
                                load_structure, verify)


@pytest.mark.parametrize("n", [1, 2, 3])
def test_structure_passes(n):
    r = verify(n, verbose=False)
    assert r["status"] == "PASS"
    assert r["triples"] == r["dim"] ** 3


def test_detects_corruption():
    """Negative control: perturbing one constant must be detected."""
    s = load_structure(1)
    basis, parity = s["basis"]["ordering"], s["parity"]
    tab = bracket_table(s["structure_constants"])
    tab[("E_2del1_p", "E_2del1_m")]["H_2"] = Fraction(3)  # true value 4
    assert check_antisymmetry(basis, parity, tab)
    tab[("E_2del1_m", "E_2del1_p")]["H_2"] = Fraction(-3)
    assert not check_antisymmetry(basis, parity, tab)
    _, fails = check_jacobi(basis, parity, tab)
    assert fails
