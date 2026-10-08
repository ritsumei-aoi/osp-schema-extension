"""Tests for I04: the verification script passes on the data and detects injected errors."""
import copy
import json
import os

import pytest

from verify_C_structure import verify, DATA_DIR


def load(n):
    with open(os.path.join(DATA_DIR, f"C_{n}_structure.json")) as fh:
        return json.load(fh)


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema1_passes(n):
    r = verify(load(n), verbose=False)
    assert r["passed"], r["failures"][:5]
    dim = 2 * n * n + 5 * n + 1
    assert r["pairs"] == dim ** 2 and r["triples"] == dim ** 3


def test_detects_broken_antisymmetry():
    d = copy.deepcopy(load(1))
    e = next(e for e in d["structure_constants"] if e["X"] == "H_2" and e["Y"] == "E_2del1_p")
    e["coeff"] = "-1"   # wrong value (should be -2)
    r = verify(d, verbose=False)
    kinds = {f[0] for f in r["failures"]}
    assert "antisymmetry" in kinds and "jacobi" in kinds


def test_detects_broken_jacobi_only():
    """Flip both (X,Y) and (Y,X) consistently so anti-symmetry still holds but Jacobi breaks."""
    d = copy.deepcopy(load(1))
    for e in d["structure_constants"]:
        if {e["X"], e["Y"]} == {"E_2del1_p", "E_2del1_m"}:
            e["coeff"] = str(-int(e["coeff"]))
    r = verify(d, verbose=False)
    kinds = {f[0] for f in r["failures"]}
    assert kinds == {"jacobi"}
