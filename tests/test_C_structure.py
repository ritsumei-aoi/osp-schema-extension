"""Tests for Schema 1 of C(n+1) (Issue I03): basis, parity, realizations, structure constants."""
import json
import os

import pytest
import sympy as sp

import C_generators as G
from oscillator_algebra import OscillatorAlgebra

NS = [1, 2, 3]


def load(n):
    path = G.structure_path(n)
    assert os.path.exists(path), f"{path} missing; run python src/C_generators.py"
    with open(path) as fh:
        return json.load(fh)


# --------------------------------------------------------------------------- basis
@pytest.mark.parametrize("n", NS)
def test_dimensions(n):
    ev, od = G.even_basis(n), G.odd_basis(n)
    assert len(ev) == 2 * n * n + n + 1
    assert len(od) == 4 * n
    assert len(set(ev + od)) == 2 * n * n + 5 * n + 1
    d = load(n)
    assert d["algebra"]["dimension"] == {"total": 2 * n * n + 5 * n + 1, "even": len(ev), "odd": len(od)}
    assert d["algebra"]["family"] == "C" and d["algebra"]["m"] == 1 and d["algebra"]["n"] == n


@pytest.mark.parametrize("n", NS)
def test_basis_labels_and_counts(n):
    ev, od = G.even_basis(n), G.odd_basis(n)
    assert ev[: n + 1] == [f"H_{k}" for k in range(1, n + 2)]
    assert sum(g.startswith("E_2del") for g in ev) == 2 * n
    assert sum(g.startswith("E_del") for g in ev) == 2 * n * (n - 1)
    assert all(g.startswith("E_eps1_del") for g in od)
    for st in ("pp", "pm", "mp", "mm"):
        assert sum(g.endswith("_" + st) for g in od) == n
    d = load(n)
    assert d["basis"]["even"] == ev and d["basis"]["odd"] == od
    assert d["basis"]["ordering_convention"].startswith("PBW: kappa < [odd] < [even]")


@pytest.mark.parametrize("n", NS)
def test_parity_table(n):
    d = load(n)
    par = d["parity"]
    assert set(par) == set(G.basis(n))
    for g, p in par.items():
        assert p == (1 if g.startswith("E_eps1_del") else 0)
    assert sum(par.values()) == 4 * n


@pytest.mark.parametrize("n", NS)
def test_oscillator_sections(n):
    d = load(n)
    og = d["oscillator_generators"]
    assert set(og) == {"fermions", "bosons"}
    assert og["fermions"]["labels"] == ["a_1_p", "a_1_m"] and og["fermions"]["m"] == 1
    assert og["bosons"]["n"] == n and len(og["bosons"]["labels"]) == 2 * n
    assert "standard_fermion_anticommutators" in d["oscillator_relations"]
    assert "supplementary_fermion" not in og
    ce = d["central_elements"]
    assert ce["kappa"]["parity"] == 1 and ce["K"]["parity"] == 0


# -------------------------------------------------------------------- realizations
@pytest.mark.parametrize("n", NS)
def test_realizations_normal_ordered_and_parity(n):
    d = load(n)
    alg = OscillatorAlgebra(n)
    reals = d["generator_realization"]["realizations"]
    assert set(reals) == set(G.basis(n))
    for g, r in reals.items():
        for term in r["standard_form"]:
            w = tuple(term["words"])
            assert alg.normal_order(w) == {w: 1}, f"{g}: word {w} not normal ordered"
            assert alg.word_parity(w) == r["parity"] == d["parity"][g]
        if not g.startswith("H_"):
            assert len(r["standard_form"]) == 1 and r["standard_form"][0]["coeff"] == "1"


@pytest.mark.parametrize("n", NS)
def test_cartan_realizations(n):
    e = G.elements(n)
    assert e["H_1"] == {("a_1_p", "a_1_m"): 1, ("b_1_p", "b_1_m"): 1}
    assert e[f"H_{n + 1}"] == {(f"b_{n}_p", f"b_{n}_m"): -1, (): sp.Rational(-1, 2)}
    for k in range(2, n + 1):
        assert e[f"H_{k}"] == {(f"b_{k - 1}_p", f"b_{k - 1}_m"): 1, (f"b_{k}_p", f"b_{k}_m"): -1}


# --------------------------------------------------------------- structure constants
def bracket_table(d):
    tab = {}
    for e in d["structure_constants"]:
        tab.setdefault((e["X"], e["Y"]), {})[e["Z"]] = sp.Rational(e["coeff"])
    return tab


@pytest.mark.parametrize("n", NS)
def test_structure_constants_conform_to_spec(n):
    d = load(n)
    labels = set(G.basis(n))
    par, roots = d["parity"], d["roots"]["vectors"]
    seen = set()
    for e in d["structure_constants"]:
        assert e["X"] in labels and e["Y"] in labels and e["Z"] in labels
        assert e["sign_rule"] == "graded"
        sp.Rational(e["coeff"])  # parses
        assert e["coeff"] != "0"
        assert par[e["Z"]] == (par[e["X"]] + par[e["Y"]]) % 2
        assert [a + b for a, b in zip(roots[e["X"]], roots[e["Y"]])] == roots[e["Z"]]
        key = (e["X"], e["Y"], e["Z"])
        assert key not in seen, f"duplicate entry {key}"
        seen.add(key)


@pytest.mark.parametrize("n", NS)
def test_structure_constants_match_recomputation(n):
    d = load(n)
    fresh = G.structure_constants(n)
    assert fresh == d["structure_constants"]


@pytest.mark.parametrize("n", NS)
def test_graded_antisymmetry(n):
    d = load(n)
    tab, par = bracket_table(d), d["parity"]
    B = G.basis(n)
    for X in B:
        for Y in B:
            sign = -1 if (par[X] and par[Y]) else 1
            lhs = tab.get((X, Y), {})
            rhs = {Z: -sign * c for Z, c in tab.get((Y, X), {}).items()}
            assert lhs == rhs, (X, Y)


@pytest.mark.parametrize("n", NS)
def test_selected_brackets(n):
    """Hand-checked values (see I01/I03 responses)."""
    tab = bracket_table(load(n))
    assert tab[("E_2del1_p", "E_2del1_m")] == ({"H_2": 4} if n == 1 else
                                              {f"H_{k}": -4 for k in range(2, n + 1)} | {f"H_{n + 1}": 4})
    assert tab[(f"E_2del{n}_p", f"E_2del{n}_m")] == {f"H_{n + 1}": 4}
    assert tab[("H_1", "E_eps1_del1_pp")] == {"E_eps1_del1_pp": 2}
    # {a^+ b_k^-, a^- b_k^+} = N_a + N_k ;  for k = 1 this is H_1
    assert tab[("E_eps1_del1_pm", "E_eps1_del1_mp")] == {"H_1": 1}
    # [H_{n+1}, E_2del{n}_p] = -2 E_2del{n}_p
    assert tab[(f"H_{n + 1}", f"E_2del{n}_p")] == {f"E_2del{n}_p": -2}


@pytest.mark.parametrize("n", NS)
def test_cartan_is_abelian_and_diagonal(n):
    d = load(n)
    tab = bracket_table(d)
    roots = d["roots"]["vectors"]
    for i in range(1, n + 2):
        for j in range(1, n + 2):
            assert (f"H_{i}", f"H_{j}") not in tab
        for g in G.basis(n):
            if not g.startswith("H_"):
                br = tab.get((f"H_{i}", g), {})
                assert set(br) <= {g}, (i, g, br)  # root vectors are weight vectors
    # every root vector has a non-zero weight for at least one Cartan element
    for g in G.basis(n):
        if not g.startswith("H_"):
            assert any(tab.get((f"H_{i}", g)) for i in range(1, n + 2)), g
