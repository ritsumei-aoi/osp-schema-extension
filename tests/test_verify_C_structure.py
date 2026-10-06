import copy
import os
import sys
from fractions import Fraction

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import verify_C_structure as V  # noqa: E402


@pytest.mark.parametrize("n", [1, 2, 3])
def test_all_checks_pass(n):
    r = V.verify(n)
    assert r["antisym_failures"] == []
    assert r["jacobi_failures"] == []
    assert r["triples"] == r["dim"] ** 3


def test_checker_detects_corruption():
    names, par, br = V.load(1)
    bad = copy.deepcopy(br)
    key = ("E_eps1_del1_pp", "E_eps1_del1_mm")
    bad[key]["H_1"] += Fraction(1)
    assert V.check_antisymmetry(names, par, bad)
    assert V.check_jacobi(names, par, bad)[1]
    bad2 = copy.deepcopy(br)
    bad2[("H_1", "E_2del1_p")]["E_2del1_p"] = Fraction(3)  # keep antisymmetry broken & Jacobi broken
    assert V.check_jacobi(names, par, bad2)[1]
