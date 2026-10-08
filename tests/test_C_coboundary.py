"""Issue I07: Schema 4 (coboundary structure) tests."""
import json
import os
import random
from fractions import Fraction

import pytest

import C_coboundary as CB
import C_gamma as CG
import C_generators as G
import verify_C_structure as V

NS = [1, 2, 3]


def load(n):
    assert os.path.exists(CB.coboundary_path(n)), "run python src/C_coboundary.py"
    return CB.load_schema4(n)


def random_phi(labels, seed):
    rng = random.Random(seed)
    return {lab: Fraction(rng.randint(-3, 3), rng.randint(1, 2)) for lab in labels}


@pytest.mark.parametrize("n", NS)
def test_parameter_set(n):
    d = load(n)
    par = json.load(open(G.structure_path(n)))["parity"]
    par["K"] = 0
    params = d["odd_linear_map"]["parameters"]
    n_even, n_odd = 2 * n * n + n + 1, 4 * n
    assert len(params) == n_even * n_odd + n_odd * (n_even + 1) == d["odd_linear_map"]["parameter_count"]
    labels = set(G.basis(n))
    for p in params:
        assert p["from"] in labels and (p["to"] in labels or p["to"] == "K")
        assert par[p["to"]] == 1 - par[p["from"]]  # f is odd
        assert p["label"] == CB.phi_label(p["to"], p["from"])
    assert len({p["label"] for p in params}) == len(params)


@pytest.mark.parametrize("n", NS)
def test_entries_consistent_with_layer1_basis(n):
    d = load(n)
    par = json.load(open(G.structure_path(n)))["parity"]
    par["K"] = 0
    labels = set(G.basis(n))
    plabels = {p["label"] for p in d["odd_linear_map"]["parameters"]}
    for e in d["coboundary"]["entries"]:
        assert e["X"] in labels and e["Y"] in labels and (e["Z"] in labels or e["Z"] == "K")
        assert par[e["Z"]] == (par[e["X"]] + par[e["Y"]] + 1) % 2
        assert e["linear_form"] and set(e["linear_form"]) <= plabels
        assert all(Fraction(c) != 0 for c in e["linear_form"].values())


@pytest.mark.parametrize("n", NS)
def test_matches_recomputation(n):
    d = load(n)
    fresh = CB.build_schema4(n)
    assert fresh["coboundary"]["entries"] == d["coboundary"]["entries"]


@pytest.mark.parametrize("n", NS)
def test_delta_f_is_graded_antisymmetric(n):
    d = load(n)
    cochain = CB.cochain_from_schema4(d)
    phi = random_phi([p["label"] for p in d["odd_linear_map"]["parameters"]], seed=n)
    tab = CB.CoboundaryOperator.evaluate(cochain, phi)
    par = json.load(open(G.structure_path(n)))["parity"]
    for X in G.basis(n):
        for Y in G.basis(n):
            sign = -1 if (par[X] and par[Y]) else 1
            lhs = tab.get((X, Y), {})
            rhs = {Z: -sign * c for Z, c in tab.get((Y, X), {}).items()}
            assert lhs == rhs, (X, Y)


@pytest.mark.parametrize("n", NS)
def test_delta_f_is_a_cocycle(n):
    """delta(delta f) = 0: the algebra g~ (+) kappa g~ deformed by gamma := delta f satisfies super Jacobi."""
    d = load(n)
    cochain = CB.cochain_from_schema4(d)
    phi = random_phi([p["label"] for p in d["odd_linear_map"]["parameters"]], seed=20 + n)
    tab = CB.CoboundaryOperator.evaluate(cochain, phi)
    s1 = json.load(open(G.structure_path(n)))
    fake_s2 = {"inhomogeneous_deformation": {"gamma": [
        {"X": X, "Y": Y, "Z": Z, "linear_form": {"t": str(c)}} for (X, Y), comp in tab.items() for Z, c in comp.items()]}}
    basis, parity, table = CG.extended_algebra(n, {"t": Fraction(1)}, s1, fake_s2)
    res = V.verify(basis, parity, table)
    assert res["pass"], res["jacobi_failures"][:3]


def test_hand_checked_delta_f_n1():
    """X = E_eps1_del1_pp (odd), [X, X} = 0, so
    (delta f)(X, X) = (-1)^1 [X, f(X)] - (-1)^{(1+1)*1} [X, f(X)] = -2 [X, f(X)].
    With f(X) = phi_H1 H_1 + phi_H2 H_2 + phi_p E_2del1_p + phi_m E_2del1_m + phi_K K and
    [X, H_1] = -2X, [X, H_2] = X, [X, E_2del1_p] = 0, [X, E_2del1_m] = -2 E_eps1_del1_pm, [X, K] = 0:
    (delta f)(X, X) = (4 phi_H1 - 2 phi_H2) X + 4 phi_m E_eps1_del1_pm."""
    op = CB.CoboundaryOperator(1)
    X = "E_eps1_del1_pp"
    lf = op.delta_f(X, X)
    assert lf == {
        X: {CB.phi_label("H_1", X): Fraction(4), CB.phi_label("H_2", X): Fraction(-2)},
        "E_eps1_del1_pm": {CB.phi_label("E_2del1_m", X): Fraction(4)},
    }
