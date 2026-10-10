"""I06: Schema 3 evaluated-structure tests."""

import json
import os
import sys
from fractions import Fraction

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from C_evaluate import check_against_schema2, evaluate_gamma
from C_gamma import gb_labels

DATA = os.path.join(os.path.dirname(__file__), "..", "data")


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema3_consistency(n):
    with open(os.path.join(DATA, f"C_{n}_evaluated.json")) as f:
        data = json.load(f)
    assert data["layer"] == 3
    assert data["algebra_ref"] == f"C_{n}_structure.json"
    assert set(data["gb_assignment"]) == set(gb_labels(n))
    assert all(Fraction(v) == 1 for v in data["gb_assignment"].values())
    assert check_against_schema2(n, data)
    # every referenced Z is a basis label or K
    with open(os.path.join(DATA, f"C_{n}_structure.json")) as f:
        s1 = json.load(f)
    basis = set(s1["basis"]["even"]) | set(s1["basis"]["odd"]) | {"K"}
    for rec in data["evaluated_gamma"]:
        assert rec["Z"] in basis
        Fraction(rec["coeff"])


def test_zero_assignment_gives_zero():
    assignment = {l: Fraction(0) for l in gb_labels(1)}
    assert evaluate_gamma(1, assignment) == []
