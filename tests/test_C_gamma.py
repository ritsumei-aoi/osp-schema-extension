"""Issue I05: tests for the Schema 2 (gamma) layer."""

from __future__ import annotations

import json
import os
import sys

import pytest
import sympy as sp

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "src"))

import C_gamma as cg  # noqa: E402
from osc_algebra import CAlgebra, gb_symbols  # noqa: E402

NS = [1, 2, 3]


@pytest.fixture(scope="module")
def docs():
    out = {}
    for n in NS:
        path = os.path.join(REPO, "data", f"C_{n}_gamma.json")
        if not os.path.exists(path):
            cg.write_schema2(n)
        with open(path) as fh:
            out[n] = json.load(fh)
    return out


@pytest.mark.parametrize("n", NS)
def test_gb_matrix_shape(docs, n):
    gm = docs[n]["gb_matrix"]
    assert gm["shape"] == [2, 2 * n]
    assert gm["count"] == 4 * n == len(gm["parameters"])
    assert len(set(gm["parameters"])) == 4 * n
    assert gm["rows"] == ["a_1_p", "a_1_m"]
    assert len(gm["cols"]) == 2 * n


@pytest.mark.parametrize("n", NS)
def test_undeformed_part_unchanged(docs, n):
    assert docs[n]["consistency"]["undeformed_part_matches_schema1"] is True
    assert docs[n]["consistency"]["undeformed_mismatches"] == []


@pytest.mark.parametrize("n", NS)
def test_cocycle_condition(docs, n):
    c = docs[n]["consistency"]
    assert c["cocycle_condition_holds"] is True
    assert c["cocycle_triples_checked"] == (2 * n * n + 5 * n + 1) ** 3


@pytest.mark.parametrize("n", NS)
def test_gamma_is_linear_in_gb(docs, n):
    """Every gamma coefficient is a homogeneous degree-1 polynomial in gb."""
    params = {sp.Symbol(p) for p in docs[n]["gb_matrix"]["parameters"]}
    for e in docs[n]["inhomogeneous_deformation"]["entries"]:
        expr = sp.expand(sp.sympify(e["coeff"]))
        poly = sp.Poly(expr, *sorted(params, key=str))
        assert poly.total_degree() == 1
        assert all(sum(m) == 1 for m in poly.monoms())


@pytest.mark.parametrize("n", NS)
def test_gamma_parity(docs, n):
    """p(gamma(X,Y)) = p(X) + p(Y) + 1  (kappa is odd)."""
    doc = docs[n]
    par = dict(doc["parity"])
    par["K"] = 0
    for e in doc["inhomogeneous_deformation"]["entries"]:
        assert par[e["Z"]] == (e["parity_X"] + e["parity_Y"] + 1) % 2, e


@pytest.mark.parametrize("n", NS)
def test_gamma_vanishes_on_purely_bosonic_pairs(docs, n):
    """gamma needs a fermion: it vanishes unless X or Y involves a_1^+-."""
    doc = docs[n]
    for e in doc["inhomogeneous_deformation"]["entries"]:
        involves_fermion = [
            lab.startswith("E_eps1_") or lab == "H_eps1" for lab in (e["X"], e["Y"])
        ]
        assert any(involves_fermion), e


@pytest.mark.parametrize("n", NS)
def test_gamma_matches_live_computation(docs, n):
    gb, _ = gb_symbols(n)
    alg = CAlgebra(n, gb)
    live = {}
    for i, x in enumerate(alg.pbw_order):
        for y in alg.pbw_order[i:]:
            _free, kap = alg.split_kappa(alg.bracket_labels(x, y))
            if kap:
                for z, c in alg.decompose_kappa(kap).items():
                    live[(x, y, z)] = sp.expand(c)
    from_json = {
        (e["X"], e["Y"], e["Z"]): sp.expand(sp.sympify(e["coeff"]))
        for e in docs[n]["inhomogeneous_deformation"]["entries"]
    }
    assert from_json == live


def test_gamma_hand_checked_entry(docs):
    """gamma(E_eps1_del1_pp, H_del1) = gb_a1P_b1P (H_del1 + K/2) + gb_a1P_b1M E_2del1_p."""
    entries = {
        (e["X"], e["Y"], e["Z"]): sp.sympify(e["coeff"])
        for e in docs[1]["inhomogeneous_deformation"]["entries"]
    }
    P, M = sp.Symbol("gb_a1P_b1P"), sp.Symbol("gb_a1P_b1M")
    assert entries[("E_eps1_del1_pp", "H_del1", "H_del1")] == P
    assert entries[("E_eps1_del1_pp", "H_del1", "K")] == P / 2
    assert entries[("E_eps1_del1_pp", "H_del1", "E_2del1_p")] == M
