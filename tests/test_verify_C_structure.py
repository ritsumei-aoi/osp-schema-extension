"""I04 tests: antisymmetry + super Jacobi on the Schema 1 JSON files, with a negative control."""
import copy
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from verify_C_structure import BracketTable, verify  # noqa: E402


@pytest.mark.parametrize("n", [1, 2, 3])
def test_structure_passes(n):
    rep = verify(BracketTable.load(n), verbose=False)
    assert rep["pass"], rep
    N = rep["n_basis"]
    assert rep["pairs_checked"] == N * N and rep["triples_checked"] == N ** 3


def test_negative_control_detects_corruption():
    data = json.load(open(os.path.join(ROOT, "data", "C_1_structure.json")))
    bad = copy.deepcopy(data)
    # flip the sign of one structure constant -> antisymmetry and Jacobi must break
    bad["structure_constants"][0]["coeff"] = str(-int(bad["structure_constants"][0]["coeff"]))
    rep = verify(BracketTable(bad), verbose=False)
    assert not rep["pass"]
    assert rep["antisymmetry_failures"]
    assert rep["jacobi_failures"]
