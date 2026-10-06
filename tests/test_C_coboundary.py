"""Issue I07: tests for the Schema 4 (coboundary) layer."""

from __future__ import annotations

import json
import os
import sys

import pytest
import sympy as sp

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "src"))

import C_coboundary as cb  # noqa: E402
from C_gamma import build_gamma, gamma_table  # noqa: E402
from osc_algebra import CAlgebra, gb_symbols  # noqa: E402

NS = [1, 2, 3]


def load(n):
    path = os.path.join(REPO, "data", f"C_{n}_coboundary.json")
    if not os.path.exists(path):
        cb.write_schema4(n)
    with open(path) as fh:
        return json.load(fh)


@pytest.mark.parametrize("n", NS)
def test_f_is_parity_reversing(n):
    doc = load(n)
    assert doc["consistency"]["f_is_parity_reversing"] is True
    par = dict(doc["parity"])
    par["K"] = 0
    for src, img in doc["f_map"]["phi"].items():
        for tgt in img:
            assert par[tgt] == (par[src] + 1) % 2, (src, tgt)


@pytest.mark.parametrize("n", NS)
def test_delta_f_equals_gamma(n):
    doc = load(n)
    assert doc["consistency"]["delta_f_equals_gamma"] is True
    assert doc["consistency"]["mismatches"] == []
    N = 2 * n * n + 5 * n + 1
    assert doc["consistency"]["pairs_compared"] == N * (N + 1) // 2


@pytest.mark.parametrize("n", NS)
def test_K_target_is_necessary(n):
    """Dropping the K-component of f breaks exactly the K-carrying pairs."""
    doc = load(n)
    assert doc["consistency"]["K_target_is_necessary"] is True
    # exactly the pairs on which delta f carries a K-component break
    assert (doc["consistency"]["mismatches_if_K_target_removed"]
            == doc["coboundary"]["K_component_entries"])
    assert doc["coboundary"]["K_component_entries"] > 0


@pytest.mark.parametrize("n", NS)
def test_coboundary_entries_match_gamma_file(n):
    with open(os.path.join(REPO, "data", f"C_{n}_gamma.json")) as fh:
        g = json.load(fh)
    gamma = {(e["X"], e["Y"], e["Z"]): sp.expand(sp.sympify(e["coeff"]))
             for e in g["inhomogeneous_deformation"]["entries"]}
    delta = {(e["X"], e["Y"], e["Z"]): sp.expand(sp.sympify(e["coeff"]))
             for e in load(n)["coboundary"]["entries"]}
    assert delta == gamma


@pytest.mark.parametrize("n", NS)
def test_f_nonzero_sources_are_odd_block_plus_H_eps1(n):
    """f vanishes on every purely bosonic even generator."""
    doc = load(n)
    expected = set(doc["basis"]["odd"]) | {"H_eps1"}
    assert set(doc["f_map"]["phi"]) == expected
    assert doc["f_map"]["nonzero_sources"] == 4 * n + 1


@pytest.mark.parametrize("n", [1, 2])
def test_delta_f_graded_antisymmetry_for_arbitrary_phi(n):
    """delta f is graded antisymmetric for *any* odd phi, not just the canonical one."""
    cob = cb.Coboundary(n)
    rng = sp.Integer
    phi = {}
    for j, src in enumerate(cob.order):
        targets = [t for t in cob.order if cob.par[t] != cob.par[src]] + ["K"]
        img = {}
        for i, t in enumerate(targets):
            if t == "K" and cob.par[src] != 1:
                continue
            img[t] = rng((i * 7 + j * 3) % 11 - 5)
        phi[src] = {k: v for k, v in img.items() if v != 0}
    assert cob.check_f_is_odd(phi) == []

    for x in cob.order:
        for y in cob.order:
            s = -1 if (cob.par[x] and cob.par[y]) else 1
            lhs = cob.delta_f(phi, x, y)
            rhs = {k: sp.expand(-s * v) for k, v in cob.delta_f(phi, y, x).items()}
            assert cb.vadd(lhs, rhs, -1) == {}, (x, y)


@pytest.mark.parametrize("n", NS)
def test_canonical_f_reconstructs_gamma_live(n):
    """End-to-end: build f and gamma from scratch and compare, bypassing JSON."""
    gb, _ = gb_symbols(n)
    cob = cb.Coboundary(n)
    phi = cb.canonical_f(n, gb)
    _a, _p, entries, _c, _l = build_gamma(n)
    gam = gamma_table(CAlgebra(n, gb), entries)
    for i, x in enumerate(cob.order):
        for y in cob.order[i:]:
            assert cb.vadd(cob.delta_f(phi, x, y), gam[(x, y)], -1) == {}, (x, y)


@pytest.mark.parametrize("n", NS)
def test_schema4_shares_basis_with_schema1(n):
    with open(os.path.join(REPO, "data", f"C_{n}_structure.json")) as fh:
        doc1 = json.load(fh)
    doc4 = load(n)
    assert doc4["basis"]["pbw_order"] == doc1["basis"]["pbw_order"]
    assert doc4["parity"] == doc1["parity"]
    assert doc4["algebra"] == doc1["algebra"]
