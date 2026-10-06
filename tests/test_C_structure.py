"""Unit tests for the C(n+1) Schema-1 structure (Issue I03)."""

import json
import os
import sys

import pytest
import sympy as sp

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

import osc_algebra as oa
import C_generators as cg

NS = (1, 2, 3)


def load(n):
    with open(os.path.join(ROOT, "data", f"C_{n}_structure.json")) as f:
        return json.load(f)


@pytest.mark.parametrize("n", NS)
def test_dimensions(n):
    d = load(n)
    dim = d["algebra"]["dimension"]
    assert dim["even"] == 2 * n ** 2 + n + 1
    assert dim["odd"] == 4 * n
    assert dim["total"] == 2 * n ** 2 + 5 * n + 1
    assert len(d["basis"]["even"]) == dim["even"]
    assert len(d["basis"]["odd"]) == dim["odd"]


@pytest.mark.parametrize("n", NS)
def test_generator_counts(n):
    d = load(n)
    # n+1 Cartan, 2n of E_2del, 2n(n-1) of E_del_del, => even = 2n^2+n+1
    cartan = [l for l in d["basis"]["even"] if l.startswith("H_")]
    assert len(cartan) == n + 1
    e2 = [l for l in d["basis"]["even"] if l.startswith("E_2del")]
    assert len(e2) == 2 * n
    edd = [l for l in d["basis"]["even"] if l.startswith("E_del")]
    assert len(edd) == 2 * n * (n - 1)
    assert len(d["basis"]["odd"]) == 4 * n
    assert all(l.startswith("E_eps1_del") for l in d["basis"]["odd"])


@pytest.mark.parametrize("n", NS)
def test_parity_consistency(n):
    d = load(n)
    P = d["parity"]
    for l in d["basis"]["even"]:
        assert P[l] == 0
    for l in d["basis"]["odd"]:
        assert P[l] == 1
    # every parity key is a basis label and vice versa
    assert set(P) == set(d["basis"]["even"]) | set(d["basis"]["odd"])


@pytest.mark.parametrize("n", NS)
def test_structure_constants_close_on_basis(n):
    """Every target Z is a basis label or the central K."""
    d = load(n)
    allowed = set(d["basis"]["even"]) | set(d["basis"]["odd"]) | {"K"}
    for r in d["structure_constants"]:
        assert r["X"] in allowed and r["Y"] in allowed
        assert r["Z"] in allowed
        assert r["sign_rule"] == "graded"


@pytest.mark.parametrize("n", NS)
def test_graded_antisymmetry(n):
    """[X,Y} = -(-1)^{pX pY} [Y,X}: recomputing with swapped args gives the negated/signed result."""
    R = cg.realizations(n)
    P = cg.parity_map(n)
    labels = cg.pbw_order(n)
    for i, X in enumerate(labels):
        for Y in labels[i:]:
            fwd = cg.decompose(oa.graded_commutator(R[X], P[X], R[Y], P[Y]), n)
            rev = cg.decompose(oa.graded_commutator(R[Y], P[Y], R[X], P[X]), n)
            sign = -1 if (P[X] * P[Y]) % 2 else 1
            combined = dict(fwd)
            for k, v in rev.items():
                combined[k] = combined.get(k, sp.Integer(0)) + sign * v
            assert all(v == 0 for v in combined.values()), (X, Y, combined)


@pytest.mark.parametrize("n", NS)
def test_cartan_commute(n):
    """Cartan generators mutually commute."""
    R = cg.realizations(n)
    P = cg.parity_map(n)
    cartan = [f"H_{i}" for i in range(1, n + 2)]
    for a in cartan:
        for b in cartan:
            res = cg.decompose(oa.graded_commutator(R[a], P[a], R[b], P[b]), n)
            assert res == {}, (a, b, res)


@pytest.mark.parametrize("n", NS)
def test_car_relation(n):
    """Sanity: the fermion satisfies {a^-,a^+}=1 and (a^±)^2=0 in the engine."""
    ap = oa.mono([oa.a_p()])
    am = oa.mono([oa.a_m()])
    anti = oa.poly_add  # noqa
    prod1 = oa.poly_mul(am, ap)
    prod2 = oa.poly_mul(ap, am)
    s = dict(prod1)
    for k, v in prod2.items():
        s[k] = s.get(k, sp.Integer(0)) + v
    s = {k: v for k, v in s.items() if v != 0}
    # {a^-,a^+} = identity (empty word)
    assert s == {(0, ()): sp.Integer(1)}
    assert oa.poly_mul(ap, ap) == {}
    assert oa.poly_mul(am, am) == {}


def test_known_values_n1():
    """Hand-verified brackets for C(2), n=1."""
    R = cg.realizations(1)
    P = cg.parity_map(1)

    def br(x, y):
        return cg.decompose(oa.graded_commutator(R[x], P[x], R[y], P[y]), 1)

    # {E_{eps+del}, E_{-eps+del}} = (b^+)^2 = E_2del1_p
    assert br("E_eps1_del1_pp", "E_eps1_del1_mp") == {"E_2del1_p": sp.Integer(1)}
    # [E_2del1_p, E_2del1_m] = 4 H_2
    assert br("E_2del1_p", "E_2del1_m") == {"H_2": sp.Integer(4)}
    # [H_1, E_2del1_p] = 2 E_2del1_p
    assert br("H_1", "E_2del1_p") == {"E_2del1_p": sp.Integer(2)}
    # {E_{eps+del}, E_{-eps-del}} = N_b - N_a + 1 = -H_1 - 2H_2
    assert br("E_eps1_del1_pp", "E_eps1_del1_mm") == {"H_1": sp.Integer(-1), "H_2": sp.Integer(-2)}
