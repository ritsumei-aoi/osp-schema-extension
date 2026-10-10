"""I05: Schema 2 gamma-structure tests."""

import json
import os
import sys
from fractions import Fraction

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from C_gamma import compute_gamma, check_consistency, gb_labels

DATA = os.path.join(os.path.dirname(__file__), "..", "data")


def load_entries(n):
    with open(os.path.join(DATA, f"C_{n}_gamma.json")) as f:
        return json.load(f)


@pytest.mark.parametrize("n", [1, 2, 3])
def test_gamma_consistency_and_determinism(n):
    data = load_entries(n)
    assert data["layer"] == 2
    assert data["gb_matrix"]["labels"] == gb_labels(n)
    assert len(data["gb_matrix"]["labels"]) == 4 * n
    entries = compute_gamma(n)
    assert data["inhomogeneous_deformation"]["entries"] == entries
    assert check_consistency(n, entries) == []


@pytest.mark.parametrize("n", [1, 2])
def test_gamma_graded_antisymmetry(n):
    """gamma(X,Y) = -(-1)^{p(X)p(Y)} gamma(Y,X), inherited from the bracket."""
    with open(os.path.join(DATA, f"C_{n}_structure.json")) as f:
        parity = json.load(f)["parity"]
    entries = load_entries(n)["inhomogeneous_deformation"]["entries"]
    table = {}
    for e in entries:
        table[(e["X"], e["Y"])] = {
            (t["gb"], t["Z"]): Fraction(t["coeff"]) for t in e["terms"]
        }
    for (x, y), terms in table.items():
        sign = -1 if (parity[x] and parity[y]) else 1
        rev = table.get((y, x), {})
        assert terms == {k: -sign * v for k, v in rev.items()}, (x, y)


def test_gamma_hand_check_n1():
    """gamma(E_eps_del1_pp, E_2del1_m) = gb_p_1_m * (2 H_1 + K), hand-derived."""
    entries = load_entries(1)["inhomogeneous_deformation"]["entries"]
    for e in entries:
        if e["X"] == "E_eps_del1_pp" and e["Y"] == "E_2del1_m":
            got = {(t["gb"], t["Z"]): t["coeff"] for t in e["terms"]}
            assert got == {("gb_p_1_m", "H_1"): "2", ("gb_p_1_m", "K"): "1"}
            return
    raise AssertionError("entry not found")
