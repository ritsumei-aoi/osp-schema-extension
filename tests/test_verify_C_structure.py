"""Tests for the Schema 1 verifier (Issue I04)."""
import copy
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from verify_C_structure import verify  # noqa: E402


def load(n):
    with open(os.path.join(ROOT, "data", f"C_{n}_structure.json"), encoding="utf-8") as fh:
        return json.load(fh)


@pytest.mark.parametrize("n", [1, 2, 3])
def test_all_checks_pass(n):
    rep = verify(load(n))
    dim = rep["dim"]
    assert rep["passed"], rep["failures"]
    assert rep["counts"]["pairs_checked"] == dim ** 2
    assert rep["counts"]["triples_checked"] == dim ** 3


def test_verifier_detects_corruption():
    doc = copy.deepcopy(load(1))
    # flip the sign of one half of an antisymmetric pair -> antisymmetry and Jacobi must fail
    for r in doc["structure_constants"]:
        if r["X"] == "H_1" and r["Y"] == "E_2del1_p":
            r["coeff"] = "-2"
    rep = verify(doc)
    assert not rep["passed"]
    assert rep["failures"]["antisymmetry"]
    assert rep["failures"]["jacobi"]


def test_verifier_detects_parity_violation():
    doc = copy.deepcopy(load(1))
    doc["structure_constants"].append({"X": "H_1", "Y": "H_2", "Z": "E_eps1_del1_pp", "coeff": "1", "sign_rule": "graded"})
    rep = verify(doc)
    assert rep["failures"]["closure_parity"]
