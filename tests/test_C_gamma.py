"""Tests for Schema 2 (gamma structure) of C(n+1) (Issue I05)."""
import json
import os
import sys
from fractions import Fraction

import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))

from C_gamma import build_schema2, check_gamma_consistency, gb_labels  # noqa: E402


def load(name):
    with open(os.path.join(ROOT, "data", name)) as fh:
        return json.load(fh)


def tables_from_json(n):
    s1 = load(f"C_{n}_structure.json")
    s2 = load(f"C_{n}_gamma.json")
    order = s1["basis"]["pbw_order"]
    par = s1["parity"]
    sc = {(X, Y): {} for X in order for Y in order}
    for e in s1["structure_constants"]:
        sc[(e["X"], e["Y"])][e["Z"]] = Fraction(e["coeff"])
    gamma = {(X, Y): {} for X in order for Y in order}
    for e in s2["inhomogeneous_deformation"]["gamma"]:
        gamma[(e["X"], e["Y"])][e["Z"]] = {l: Fraction(c) for l, c in e["coeff"].items()}
    return s2, order, par, sc, gamma


@pytest.mark.parametrize("n", [1, 2, 3])
def test_gamma_json_consistent_with_schema1(n):
    s2, order, par, sc, gamma = tables_from_json(n)
    labels = gb_labels(n)
    assert s2["source_structure"] == f"C_{n}_structure.json"
    assert s2["gb_matrix"]["shape"] == [2, 2 * n]
    assert [e["label"] for e in s2["gb_matrix"]["entries"]] == [l for l, _ in labels]
    assert s2["central_elements"]["kappa"]["parity"] == 1
    # parity, graded antisymmetry and the first-order Jacobi (cocycle) condition, from JSON only
    problems = check_gamma_consistency(order, par, sc, gamma, labels)
    assert problems == []
    # every gamma coefficient refers to a declared gb parameter
    names = {l for l, _ in labels}
    for e in s2["inhomogeneous_deformation"]["gamma"]:
        assert set(e["coeff"]) <= names and e["coeff"]
        assert e["Z"] == "K" or e["Z"] in order


def test_gamma_json_matches_generator_n1():
    schema, _ = build_schema2(1)
    data = load("C_1_gamma.json")
    schema["metadata"]["generation_date"] = data["metadata"]["generation_date"]
    assert schema == data


def test_hand_checked_gamma_n1():
    _, order, par, sc, gamma = tables_from_json(1)
    # {a^+b^+, a^+b^+} = 2 gb_{+,1,+} kappa a^+ b^+
    assert gamma[("E_eps1_del1_pp", "E_eps1_del1_pp")] == {"E_eps1_del1_pp": {"gb_a1p_b1p": Fraction(2)}}
    # [a^+b^+, H_1] kappa-part = gb_{+,1,+}(a^+a^- + b^+b^- + 1) + gb_{+,1,-}(b^+)^2
    assert gamma[("E_eps1_del1_pp", "H_1")] == {
        "H_1": {"gb_a1p_b1p": Fraction(1)},
        "E_2del1_p": {"gb_a1p_b1m": Fraction(1)},
        "K": {"gb_a1p_b1p": Fraction(1)},
    }
    # even-even pairs with both X, Y Cartan: gamma lands in the odd part
    for Z in gamma[("H_1", "H_2")]:
        assert par[Z] == 1
