"""Tests for the C(n+1) Schema-2 gamma structure (Issue I05)."""

import json
import os
import sys

import pytest
import sympy as sp

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

import C_gamma as cgm
import C_generators as cg

NS = (1, 2, 3)


def load(n):
    with open(os.path.join(ROOT, "data", f"C_{n}_gamma.json")) as f:
        return json.load(f)


@pytest.mark.parametrize("n", NS)
def test_gb_count(n):
    d = load(n)
    assert d["gb_matrix"]["count"] == 4 * n
    assert len(d["gb_matrix"]["parameters"]) == 4 * n


@pytest.mark.parametrize("n", NS)
def test_consistency_with_schema1(n):
    d = load(n)
    assert d["consistency"]["kappa0_equals_schema1"] is True
    assert d["consistency"]["mismatches"] == []


@pytest.mark.parametrize("n", NS)
def test_gamma_targets_on_basis(n):
    d = load(n)
    with open(os.path.join(ROOT, "data", f"C_{n}_structure.json")) as f:
        s = json.load(f)
    allowed = set(s["basis"]["even"]) | set(s["basis"]["odd"]) | {"K"}
    for r in d["gamma"]:
        assert r["Z"] in allowed
        assert r["carrier"] == "kappa"


def test_gamma_known_value_n1():
    """gamma(E_pp,E_pp) = -2 gb_p_1_p E_pp (hand-derived)."""
    R = cg.realizations(1)
    P = cg.parity_map(1)
    br = cgm.deformed_bracket("E_eps1_del1_pp", "E_eps1_del1_pp", R, P)
    _, gam = cgm.split_kappa(br)
    comps = cg.decompose(gam, 1)
    gb = sp.Symbol("gb_p_1_p")
    assert sp.expand(comps.get("E_eps1_del1_pp", 0) + 2 * gb) == 0
    assert len(comps) == 1


def test_gamma_graded_antisymmetry_n1():
    """gamma(X,Y) = -(-1)^{pX pY} gamma(Y,X) for n=1 (cochain symmetry)."""
    R = cg.realizations(1)
    P = cg.parity_map(1)
    labels = cg.pbw_order(1)
    for X in labels:
        for Y in labels:
            _, gxy = cgm.split_kappa(cgm.deformed_bracket(X, Y, R, P))
            _, gyx = cgm.split_kappa(cgm.deformed_bracket(Y, X, R, P))
            cxy = cg.decompose(gxy, 1)
            cyx = cg.decompose(gyx, 1)
            sign = -1 if (P[X] * P[Y]) % 2 else 1
            keys = set(cxy) | set(cyx)
            for k in keys:
                assert sp.expand(cxy.get(k, 0) + sign * cyx.get(k, 0)) == 0
