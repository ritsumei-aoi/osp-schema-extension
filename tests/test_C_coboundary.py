"""I07: Schema 4 coboundary-structure tests."""

import json
import os
import sys
from fractions import Fraction

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from C_coboundary import schema4
from C_gamma import gb_labels

DATA = os.path.join(os.path.dirname(__file__), "..", "data")


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema4_conforms_and_deterministic(n):
    with open(os.path.join(DATA, f"C_{n}_coboundary.json")) as f:
        data = json.load(f)
    assert data["layer"] == 4
    assert set(data["gb_assignment"]) == set(gb_labels(n))
    fresh = schema4(n)  # internal asserts check basis/parity consistency
    assert data["f_map"]["entries"] == fresh["f_map"]["entries"]
    assert data["coboundary"] == fresh["coboundary"]


@pytest.mark.parametrize("n", [1, 2, 3])
def test_f_is_odd_map(n):
    with open(os.path.join(DATA, f"C_{n}_coboundary.json")) as f:
        data = json.load(f)
    with open(os.path.join(DATA, f"C_{n}_structure.json")) as f:
        parity = json.load(f)["parity"]
    parity["K"] = 0
    for e in data["f_map"]["entries"]:
        assert parity[e["target"]] == (parity[e["source"]] + 1) % 2


def test_zero_gb_gives_zero_coboundary():
    assignment = {l: Fraction(0) for l in gb_labels(1)}
    data = schema4(1, "zero", assignment)
    assert data["coboundary"] == []
    assert data["f_map"]["entries"] == []
