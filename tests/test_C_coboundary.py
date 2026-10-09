"""Tests for Schema 4 (coboundary structure) of C(n+1) (Issue I07)."""
import json
import os
import sys
from fractions import Fraction

import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))

from C_coboundary import (  # noqa: E402
    coboundary, coboundary_table, load_structure, phi_labels, phi_name, restrict_f,
)
from C_gamma import gb_labels  # noqa: E402


def load(name):
    with open(os.path.join(ROOT, "data", name)) as fh:
        return json.load(fh)


def f_lin_from_json(s4):
    f = {}
    for e in s4["candidate_map"]["f"]:
        f.setdefault(e["source"], {})[e["target"]] = {l: Fraction(c) for l, c in e["coeff"].items()}
    return f


@pytest.mark.parametrize("n", [1, 2, 3])
def test_phi_count_and_labels(n):
    s4 = load(f"C_{n}_coboundary.json")
    even, odd = 2 * n * n + n + 1, 4 * n
    assert s4["odd_map_parameterization"]["count"] == 2 * even * odd + odd
    assert s4["odd_map_parameterization"]["count_without_K_targets"] == 2 * even * odd
    _, order, par, sc = load_structure(os.path.join(ROOT, "data", f"C_{n}_structure.json"))
    assert s4["odd_map_parameterization"]["phi_labels"] == [phi_name(t, s) for t, s in phi_labels(order, par)]


@pytest.mark.parametrize("n", [1, 2])
def test_elementary_table_matches_recomputation(n):
    s4 = load(f"C_{n}_coboundary.json")
    _, order, par, sc = load_structure(os.path.join(ROOT, "data", f"C_{n}_structure.json"))
    by_phi = {}
    for e in s4["elementary_coboundaries"]["table"]:
        by_phi.setdefault(e["phi"], {}).setdefault((e["X"], e["Y"]), {})[e["Z"]] = Fraction(e["coeff"])
    idx = {l: i for i, l in enumerate(order)}
    for tgt, src in phi_labels(order, par):
        tab = coboundary_table(sc, par, order, {src: {tgt: Fraction(1)}}, all_pairs=False)
        assert tab == by_phi.get(phi_name(tgt, src), {})
        for (X, Y) in tab:
            assert idx[X] <= idx[Y]


@pytest.mark.parametrize("n", [1, 2, 3])
def test_candidate_coboundary_equals_gamma_from_json(n):
    """δ f_shift recomputed from the JSON (Schema 1 + candidate f) equals Schema 2 γ, including K."""
    s2, s4 = load(f"C_{n}_gamma.json"), load(f"C_{n}_coboundary.json")
    _, order, par, sc = load_structure(os.path.join(ROOT, "data", f"C_{n}_structure.json"))
    f_lin = f_lin_from_json(s4)
    gamma = {}
    for e in s2["inhomogeneous_deformation"]["gamma"]:
        gamma.setdefault((e["X"], e["Y"]), {})[e["Z"]] = {l: Fraction(c) for l, c in e["coeff"].items()}
    delta = {}
    for lab, _ in gb_labels(n):
        f = restrict_f(f_lin, lab)
        for (X, Y), d in coboundary_table(sc, par, order, f).items():
            for Z, c in d.items():
                delta.setdefault((X, Y), {}).setdefault(Z, {})[lab] = c
    assert delta == gamma
    assert s4["candidate_map"]["delta_f_equals_schema2_gamma"] is True
    # f_shift is odd: parity of target = parity of source + 1 (K counts as even)
    for src, tg in f_lin.items():
        for tgt in tg:
            assert (0 if tgt == "K" else par[tgt]) == (par[src] + 1) % 2
    # K-components of f_shift: f(E_{σ, k, s}) ∋ (1/2) gb_{σ,k,s} K, nothing else
    for src, tg in f_lin.items():
        if "K" in tg:
            sigma_s = src.split("_")[-1]
            k = src.split("_del")[1].split("_")[0]
            assert tg["K"] == {f"gb_a1{sigma_s[0]}_b{k}{sigma_s[1]}": Fraction(1, 2)}


def test_coboundary_formula_hand_check_n1():
    _, order, par, sc = load_structure(os.path.join(ROOT, "data", "C_1_structure.json"))
    # f: E_eps1_del1_pp -> H_1 (odd map). (δf)(H_1, E_eps1_del1_pp) = [H_1, H_1] - (-1)^{1} ... - f([H_1,E])
    f = {"E_eps1_del1_pp": {"H_1": Fraction(1)}}
    # [H_1, E_eps1_del1_pp] = 2 E_eps1_del1_pp  =>  f([H_1,E]) = 2 H_1 ; [H_1, f(E)] = [H_1,H_1] = 0 ;
    # (-1)^{(p(X)+1)p(Y)} [Y, f(X)] = [E, f(H_1)] = 0  =>  δf = -2 H_1
    assert coboundary(sc, par, f, "H_1", "E_eps1_del1_pp") == {"H_1": Fraction(-2)}
    # (δf)(E_eps1_del1_pp, E_eps1_del1_mm): (-1)^1 [E_pp, f(E_mm)] = 0 ; -(-1)^{0}[E_mm, f(E_pp)] = -[E_mm, H_1] = -2 E_mm ;
    # f([E_pp,E_mm]) = f(-H_1 - 2H_2) = 0   =>  -2 E_mm
    assert coboundary(sc, par, f, "E_eps1_del1_pp", "E_eps1_del1_mm") == {"E_eps1_del1_mm": Fraction(-2)}
