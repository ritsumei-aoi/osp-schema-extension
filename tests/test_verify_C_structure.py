import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import verify_C_structure as V  # noqa: E402


@pytest.mark.parametrize("n", [1, 2, 3])
def test_all_checks_pass(n):
    r = V.verify(n)
    assert r["triples"] == r["dim"] ** 3
    assert r["pass"], r


def test_detects_corrupted_constant():
    names, par, br = V.load_structure(1)
    key = ("E_2del1_p", "E_2del1_m")
    br[key] = {z: c * 2 for z, c in br[key].items()}
    assert V.check_antisymmetry(names, par, br) or V.check_jacobi(names, par, br)[0]
