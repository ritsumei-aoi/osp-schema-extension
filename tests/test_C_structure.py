"""Unit tests for Schema 1 of C(n+1) = osp(2|2n) (Issue I03)."""
import json
import os
import sys
from fractions import Fraction

import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))

from C_generators import (  # noqa: E402
    OscillatorAlgebra, build_algebra, build_basis, build_schema1, compute_structure_constants,
    Decomposer,
)

NS = [1, 2, 3]


def load(n):
    with open(os.path.join(ROOT, "data", f"C_{n}_structure.json")) as fh:
        return json.load(fh)


# ---------------------------------------------------------------- oscillator algebra
def test_oscillator_relations():
    alg = OscillatorAlgebra(2)
    ap, am = alg.element([(["a_1_p"], 1)]), alg.element([(["a_1_m"], 1)])
    one = {(): Fraction(1)}
    assert alg.add(alg.multiply(am, ap), alg.multiply(ap, am)) == one       # {a^-, a^+} = 1
    assert alg.multiply(ap, ap) == {} and alg.multiply(am, am) == {}       # (a^±)^2 = 0
    b1p, b1m = alg.element([(["b_1_p"], 1)]), alg.element([(["b_1_m"], 1)])
    b2p = alg.element([(["b_2_p"], 1)])
    assert alg.bracket(b1m, b1p) == one                                      # [b^-, b^+] = 1
    assert alg.bracket(b1m, b2p) == {}
    assert alg.bracket(b1p, ap) == {} and alg.bracket(b1m, am) == {}         # undeformed mixed
    # kappa: odd, central, nilpotent
    kap = alg.element([(["kappa"], 1)])
    assert alg.multiply(kap, kap) == {}
    assert alg.bracket(kap, ap) == {} and alg.bracket(kap, b1p) == {}
    assert alg.multiply(ap, kap) == {(0, 1): Fraction(-1)}                   # a kappa = -kappa a


def test_deformed_relation():
    alg = OscillatorAlgebra(1, gb={("p", 1, "m"): Fraction(3)})
    bm, ap = alg.element([(["b_1_m"], 1)]), alg.element([(["a_1_p"], 1)])
    assert alg.bracket(bm, ap) == {(0,): Fraction(-3)}                       # [b^-, a^+] = -gb kappa
    assert alg.bracket(ap, bm) == {(0,): Fraction(3)}
    assert alg.bracket(alg.element([(["b_1_p"], 1)]), ap) == {}


# ---------------------------------------------------------------- basis / counts / parity
@pytest.mark.parametrize("n", NS)
def test_generator_counts(n):
    odd, even, real, roots = build_basis(n)
    assert len(even) == 2 * n * n + n + 1
    assert len(odd) == 4 * n
    assert len(set(odd + even)) == len(odd) + len(even)
    assert all(lab.startswith("E_eps1_del") for lab in odd)
    assert [f"H_{k}" for k in range(1, n + 2)] == even[: n + 1]


@pytest.mark.parametrize("n", NS)
def test_parity_of_realizations(n):
    alg, odd, even, real, roots, elements = build_algebra(n)
    for lab in odd:
        assert alg.element_parity(elements[lab]) == 1
    for lab in even:
        assert alg.element_parity(elements[lab]) == 0


@pytest.mark.parametrize("n", NS)
def test_basis_linearly_independent(n):
    alg, odd, even, real, roots, elements = build_algebra(n)
    Decomposer(alg, odd + even, elements, include_K=True)  # raises if dependent


# ---------------------------------------------------------------- structure constants
@pytest.mark.parametrize("n", NS)
def test_closure_and_antisymmetry(n):
    entries, table = compute_structure_constants(n)
    alg, odd, even, real, roots, elements = build_algebra(n)
    par = {l: 1 for l in odd}
    par.update({l: 0 for l in even})
    for (X, Y), c in table.items():
        sign = -1 if (par[X] and par[Y]) else 1
        back = table[(Y, X)]
        assert {Z: -sign * v for Z, v in c.items()} == back
        for Z, v in c.items():
            assert (par[X] + par[Y]) % 2 == par[Z]


@pytest.mark.parametrize("n", NS)
def test_root_vectors_are_weight_vectors(n):
    """[H_i, E_alpha] = alpha(H_i) E_alpha, and [E_alpha, E_beta] ∝ E_{alpha+beta} or Cartan."""
    entries, table = compute_structure_constants(n)
    alg, odd, even, real, roots, elements = build_algebra(n)
    cartan = [f"H_{k}" for k in range(1, n + 2)]
    rootvecs = [l for l in odd + even if l not in cartan]
    weight = {}
    for E in rootvecs:
        w = []
        for H in cartan:
            c = table[(H, E)]
            assert set(c) <= {E}
            w.append(c.get(E, Fraction(0)))
        weight[E] = tuple(w)
        assert any(w), f"{E} has zero weight"
    assert len(set(weight.values())) == len(rootvecs)  # all roots distinct (multiplicity 1)
    for H in cartan:
        for H2 in cartan:
            assert table[(H, H2)] == {}
    for A in rootvecs:
        for B in rootvecs:
            target = tuple(a + b for a, b in zip(weight[A], weight[B]))
            for Z in table[(A, B)]:
                if Z in cartan:
                    assert not any(target)
                else:
                    assert weight[Z] == target


@pytest.mark.parametrize("n", NS)
def test_json_files_match_generator(n):
    data = load(n)
    fresh = build_schema1(n)
    fresh["metadata"]["generation_date"] = data["metadata"]["generation_date"]
    assert data == fresh


@pytest.mark.parametrize("n", NS)
def test_json_conforms_to_spec(n):
    d = load(n)
    for key in ["schema_version", "algebra", "oscillator_generators", "oscillator_relations",
                "central_elements", "basis", "parity", "generator_realization",
                "structure_constants", "metadata"]:
        assert key in d
    a = d["algebra"]
    assert a["family"] == "C" and a["m"] == 1 and a["n"] == n
    assert a["dimension_formula"] == {"even": "2n^2 + n + 1", "odd": "4n", "total": "2n^2 + 5n + 1"}
    assert a["dimension"] == {"even": 2 * n * n + n + 1, "odd": 4 * n, "total": 2 * n * n + 5 * n + 1}
    og = d["oscillator_generators"]
    assert set(og) == {"fermions", "bosons"}
    assert og["fermions"]["m"] == 1 and og["fermions"]["labels"] == ["a_1_p", "a_1_m"]
    assert og["bosons"]["n"] == n and len(og["bosons"]["labels"]) == 2 * n
    assert "{a_1^-, a_1^+} = 1" in d["oscillator_relations"]["fermionic_anticommutators"]["relations"]["conjugate_pair"]
    ce = d["central_elements"]
    assert ce["kappa"]["parity"] == 1 and ce["K"]["parity"] == 0
    b = d["basis"]
    assert len(b["even"]) == a["dimension"]["even"] and len(b["odd"]) == a["dimension"]["odd"]
    assert b["pbw_order"] == b["odd"] + b["even"]
    assert all(d["parity"][l] == 1 for l in b["odd"]) and all(d["parity"][l] == 0 for l in b["even"])
    assert set(d["generator_realization"]["realizations"]) == set(b["pbw_order"])
    for lab, r in d["generator_realization"]["realizations"].items():
        assert r["parity"] == d["parity"][lab]
        for t in r["standard_form"]:
            Fraction(t["coeff"])
            assert "a_0" not in t["words"]
    labels = set(b["pbw_order"])
    for e in d["structure_constants"]:
        assert e["X"] in labels and e["Y"] in labels and e["Z"] in labels
        assert e["sign_rule"] == "graded"
        Fraction(e["coeff"])
    # every ordered pair appears at most once per Z
    keys = [(e["X"], e["Y"], e["Z"]) for e in d["structure_constants"]]
    assert len(keys) == len(set(keys))


def test_hand_checked_values_n1():
    _, table = compute_structure_constants(1)
    assert table[("E_2del1_p", "E_2del1_m")] == {"H_2": Fraction(4)}
    assert table[("E_eps1_del1_pp", "E_eps1_del1_mm")] == {"H_1": Fraction(-1), "H_2": Fraction(-2)}
    assert table[("E_eps1_del1_pm", "E_eps1_del1_mp")] == {"H_1": Fraction(1)}
    assert table[("H_1", "E_eps1_del1_pp")] == {"E_eps1_del1_pp": Fraction(2)}
    assert table[("E_eps1_del1_pp", "E_eps1_del1_pp")] == {}   # 2ε is not a root
