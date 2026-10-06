"""Unit tests for the C(n+1) Schema 1 generator (Issue I03)."""

from __future__ import annotations

import json
import os
import sys

import pytest
import sympy as sp

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "src"))

from osc_algebra import CAlgebra, OscAlgebra, letter_index, word_parity  # noqa: E402
import C_generators as gen  # noqa: E402

NS = [1, 2, 3]


@pytest.fixture(scope="module")
def docs():
    out = {}
    for n in NS:
        path = os.path.join(REPO, "data", f"C_{n}_structure.json")
        if not os.path.exists(path):
            gen.write_schema1(n)
        with open(path) as fh:
            out[n] = json.load(fh)
    return out


@pytest.fixture(scope="module")
def algs():
    return {n: CAlgebra(n) for n in NS}


# --------------------------------------------------------------------------
# generator counts
# --------------------------------------------------------------------------
@pytest.mark.parametrize("n,even,odd", [(1, 4, 4), (2, 11, 8), (3, 22, 12)])
def test_dimension_counts(algs, n, even, odd):
    alg = algs[n]
    assert alg.dim_even == even == 2 * n * n + n + 1
    assert alg.dim_odd == odd == 4 * n
    assert len(alg.pbw_order) == even + odd == 2 * n * n + 5 * n + 1


@pytest.mark.parametrize("n", NS)
def test_basis_labels_unique_and_ordered(algs, n):
    alg = algs[n]
    assert len(set(alg.pbw_order)) == len(alg.pbw_order)
    # Option A: all odd generators precede all even generators
    assert alg.pbw_order[: alg.dim_odd] == alg.odd
    assert alg.pbw_order[alg.dim_odd:] == alg.even


@pytest.mark.parametrize("n", NS)
def test_odd_labels_cover_all_four_eps_roots(algs, n):
    alg = algs[n]
    expected = {
        f"E_eps1_del{k}_{suf}"
        for k in range(1, n + 1)
        for suf in ("pp", "pm", "mp", "mm")
    }
    assert set(alg.odd) == expected


# --------------------------------------------------------------------------
# parity
# --------------------------------------------------------------------------
@pytest.mark.parametrize("n", NS)
def test_parity_matches_oscillator_word_parity(algs, n):
    alg = algs[n]
    for lab in alg.pbw_order:
        for w in alg.realization[lab]:
            if w:
                assert word_parity(w) == alg.parity[lab], (lab, w)


@pytest.mark.parametrize("n", NS)
def test_parity_of_brackets_is_additive(algs, n):
    """p([X,Y}) = p(X) + p(Y) mod 2 for every non-zero structure constant."""
    alg = algs[n]
    for x in alg.pbw_order:
        for y in alg.pbw_order:
            for z, c in alg.bracket_coeffs(x, y).items():
                if z == "K":
                    continue
                assert alg.parity[z] == (alg.parity[x] + alg.parity[y]) % 2, (x, y, z, c)


# --------------------------------------------------------------------------
# normal ordering engine
# --------------------------------------------------------------------------
def test_fermion_car():
    osc = OscAlgebra(1)
    # a^- a^+ = 1 - a^+ a^-
    assert osc.normalize(("a_1_m", "a_1_p")) == {
        (): sp.Integer(1),
        ("a_1_p", "a_1_m"): sp.Integer(-1),
    }
    # (a^+)^2 = 0
    assert osc.normalize(("a_1_p", "a_1_p")) == {}
    assert osc.normalize(("a_1_m", "a_1_m")) == {}


def test_boson_ccr():
    osc = OscAlgebra(2)
    assert osc.normalize(("b_1_m", "b_1_p")) == {
        (): sp.Integer(1),
        ("b_1_p", "b_1_m"): sp.Integer(1),
    }
    # distinct indices commute
    assert osc.normalize(("b_2_m", "b_1_p")) == {("b_1_p", "b_2_m"): sp.Integer(1)}


def test_boson_fermion_commute_undeformed():
    osc = OscAlgebra(1)
    assert osc.normalize(("b_1_p", "a_1_m")) == {("a_1_m", "b_1_p"): sp.Integer(1)}


def test_letter_index_order():
    assert letter_index("kappa") == 0 < letter_index("a_1_p") == 1
    assert letter_index("a_1_m") == 2 < letter_index("b_1_p") == 3
    assert letter_index("b_1_m") == 4 < letter_index("b_2_p") == 5


def test_kappa_is_nilpotent_and_supercentral():
    osc = OscAlgebra(1)
    assert osc.normalize(("kappa", "kappa")) == {}
    # kappa anticommutes past an odd letter
    assert osc.normalize(("a_1_p", "kappa")) == {("kappa", "a_1_p"): sp.Integer(-1)}
    # and commutes past an even letter
    assert osc.normalize(("b_1_p", "kappa")) == {("kappa", "b_1_p"): sp.Integer(1)}


# --------------------------------------------------------------------------
# consistency: brackets close, no K leakage
# --------------------------------------------------------------------------
@pytest.mark.parametrize("n", NS)
def test_brackets_close_on_the_basis_without_K(algs, n):
    alg = algs[n]
    for i, x in enumerate(alg.pbw_order):
        for y in alg.pbw_order[i:]:
            coeffs = alg.bracket_coeffs(x, y)  # raises if outside the span
            assert "K" not in coeffs, (x, y, coeffs)


@pytest.mark.parametrize("n", NS)
def test_known_sl2_triples(algs, n):
    """[H_del_k, E_2del_k_p] = 2 E, [H,E_m] = -2 E_m, [E_p,E_m] = -4 H."""
    alg = algs[n]
    for k in range(1, n + 1):
        h, ep, em = f"H_del{k}", f"E_2del{k}_p", f"E_2del{k}_m"
        assert alg.bracket_coeffs(h, ep) == {ep: sp.Integer(2)}
        assert alg.bracket_coeffs(h, em) == {em: sp.Integer(-2)}
        assert alg.bracket_coeffs(ep, em) == {h: sp.Integer(-4)}


@pytest.mark.parametrize("n", NS)
def test_cartan_is_abelian(algs, n):
    alg = algs[n]
    cartan = ["H_eps1"] + [f"H_del{k}" for k in range(1, n + 1)]
    for x in cartan:
        for y in cartan:
            assert alg.bracket_coeffs(x, y) == {}


@pytest.mark.parametrize("n", NS)
def test_cartan_eigenvalues_match_roots(algs, n):
    """[H_eps1, E] and [H_del_k, E] reproduce the declared root of E."""
    alg = algs[n]
    for k in range(1, n + 1):
        for suf, eps_c, del_c in (
            ("pp", 1, 1), ("pm", 1, -1), ("mp", -1, 1), ("mm", -1, -1)
        ):
            lab = f"E_eps1_del{k}_{suf}"
            assert alg.bracket_coeffs("H_eps1", lab) == {lab: sp.Integer(eps_c)}
            assert alg.bracket_coeffs(f"H_del{k}", lab) == {lab: sp.Integer(del_c)}
            for other in range(1, n + 1):
                if other != k:
                    assert alg.bracket_coeffs(f"H_del{other}", lab) == {}


@pytest.mark.parametrize("n", NS)
def test_odd_odd_anticommutator_closes_on_even(algs, n):
    alg = algs[n]
    for x in alg.odd:
        for y in alg.odd:
            for z in alg.bracket_coeffs(x, y):
                assert z in alg.even, (x, y, z)


# --------------------------------------------------------------------------
# JSON conformance to docs/json_schema_specification.md
# --------------------------------------------------------------------------
@pytest.mark.parametrize("n", NS)
def test_json_top_level_keys(docs, n):
    doc = docs[n]
    assert set(doc) == {
        "schema_version", "layer", "algebra", "oscillator_generators",
        "oscillator_relations", "central_elements", "basis", "parity",
        "generator_realization", "structure_constants", "metadata",
    }
    assert doc["schema_version"] == "5.0"


@pytest.mark.parametrize("n", NS)
def test_json_algebra_field(docs, n):
    a = docs[n]["algebra"]
    assert a["family"] == "C" and a["m"] == 1 and a["n"] == n
    assert a["cartan_type"] == f"C({n + 1})"
    assert a["dimension"]["even"] == 2 * n * n + n + 1
    assert a["dimension"]["odd"] == 4 * n
    assert a["dimension"]["total"] == 2 * n * n + 5 * n + 1
    assert a["dimension_formulas"] == {
        "even": "2n^2 + n + 1", "odd": "4n", "total": "2n^2 + 5n + 1"
    }


@pytest.mark.parametrize("n", NS)
def test_json_oscillator_generators_and_central_elements(docs, n):
    og = docs[n]["oscillator_generators"]
    assert set(og) == {"fermions", "bosons"}
    assert og["fermions"]["m"] == 1
    assert og["fermions"]["labels"] == ["a_1_p", "a_1_m"]
    assert og["bosons"]["n"] == n and og["bosons"]["count"] == 2 * n
    assert "supplementary_fermion" not in og

    ce = docs[n]["central_elements"]
    assert ce["kappa"]["parity"] == 1
    assert ce["K"]["parity"] == 0
    assert ce["kappa"]["in_basis"] is False and ce["K"]["in_basis"] is False


@pytest.mark.parametrize("n", NS)
def test_json_basis_and_parity_consistent(docs, n):
    doc = docs[n]
    b = doc["basis"]
    assert b["pbw_order"] == b["odd"] + b["even"]
    assert set(doc["parity"]) == set(b["pbw_order"])
    assert all(doc["parity"][x] == 1 for x in b["odd"])
    assert all(doc["parity"][x] == 0 for x in b["even"])
    assert "kappa" not in b["pbw_order"] and "K" not in b["pbw_order"]


@pytest.mark.parametrize("n", NS)
def test_json_realizations_cover_basis(docs, n):
    doc = docs[n]
    r = doc["generator_realization"]["realizations"]
    assert set(r) == set(doc["basis"]["pbw_order"])
    for lab, entry in r.items():
        assert entry["parity"] == doc["parity"][lab]
        assert entry["standard_form"]
        assert "a_0" not in entry["frappat_form"]


@pytest.mark.parametrize("n", NS)
def test_json_structure_constants_wellformed(docs, n):
    doc = docs[n]
    order = doc["basis"]["pbw_order"]
    idx = {lab: i for i, lab in enumerate(order)}
    seen = set()
    for e in doc["structure_constants"]:
        assert set(e) == {"X", "Y", "Z", "coeff", "sign_rule"}
        assert idx[e["X"]] <= idx[e["Y"]], "storage convention violated"
        assert e["Z"] in idx or e["Z"] == "K"
        assert sp.nsimplify(e["coeff"]) != 0
        assert (e["X"], e["Y"], e["Z"]) not in seen
        seen.add((e["X"], e["Y"], e["Z"]))


@pytest.mark.parametrize("n", NS)
def test_json_matches_live_computation(docs, algs, n):
    """Every JSON entry reproduces the engine's bracket, and vice versa."""
    doc, alg = docs[n], algs[n]
    from_json = {
        (e["X"], e["Y"], e["Z"]): sp.nsimplify(e["coeff"])
        for e in doc["structure_constants"]
    }
    live = {}
    for i, x in enumerate(alg.pbw_order):
        for y in alg.pbw_order[i:]:
            for z, c in alg.bracket_coeffs(x, y).items():
                live[(x, y, z)] = c
    assert from_json == live
