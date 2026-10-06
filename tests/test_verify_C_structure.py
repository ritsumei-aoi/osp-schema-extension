import copy
import json
import os

import pytest

from verify_C_structure import DATA_DIR, verify


def load(n):
    with open(os.path.join(DATA_DIR, f"C_{n}_structure.json")) as fh:
        return json.load(fh)


@pytest.mark.parametrize("n", [1, 2, 3])
def test_structure_passes(n):
    r = verify(load(n))
    assert r["passed"]
    d = r["dim"]
    assert r["pairs"] == d * d and r["triples"] == d ** 3


def test_negative_control_detects_corruption():
    s = copy.deepcopy(load(1))
    # corrupt one coefficient of a bracket: both checks must notice
    for e in s["structure_constants"]:
        if (e["X"], e["Y"]) == ("E_2del1_p", "E_2del1_m"):
            e["coeff"] = "3"
    r = verify(s)
    assert not r["passed"]
    assert r["antisymmetry_failures"] and r["jacobi_failures"]
