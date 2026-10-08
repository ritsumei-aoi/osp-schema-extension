"""Tests for I03: basis, parity, counts, oscillator algebra and Schema 1 output."""
import json
import os
from fractions import Fraction

import pytest

from oscillator_algebra import OscillatorAlgebra, Poly, element_to_str
from C_generators import CBasis, build_schema1, dimension, even_labels, odd_labels, DATA_DIR

NS = [1, 2, 3]


# ---------------------------------------------------------------- Poly
def test_poly_arithmetic_and_strings():
    x, y = Poly.var("x"), Poly.var("y")
    p = (x + 1) * (y - Fraction(1, 2))
    assert str(p) == "-1/2 - 1/2*x + y + x*y"
    assert p.subs({"x": 1, "y": 2}) == Poly.const(3)
    assert Poly.from_terms_dict(p.to_terms_dict()) == p
    assert str(Poly()) == "0"


# ---------------------------------------------------------------- oscillator relations
@pytest.mark.parametrize("n", NS)
def test_oscillator_relations(n):
    A = OscillatorAlgebra(n)
    one = {(): Poly.const(1)}

    def w(*g):
        return {tuple(g): Poly.const(1)}

    # CAR
    assert A.bracket(w("a_1_m"), w("a_1_p"), 1, 1) == one
    assert A.mul(w("a_1_p"), w("a_1_p")) == {}
    assert A.mul(w("a_1_m"), w("a_1_m")) == {}
    # CCR
    for k in range(1, n + 1):
        assert A.bracket(w(f"b_{k}_m"), w(f"b_{k}_p"), 0, 0) == one
        for l in range(1, n + 1):
            if l != k:
                assert A.bracket(w(f"b_{k}_m"), w(f"b_{l}_p"), 0, 0) == {}
            assert A.bracket(w(f"b_{k}_p"), w(f"b_{l}_p"), 0, 0) == {}
        # undeformed mixed relations
        for s in "pm":
            for a in ("a_1_p", "a_1_m"):
                assert A.bracket(w(f"b_{k}_{s}"), w(a), 0, 1) == {}
    # kappa odd, nilpotent, super-central
    assert A.mul(w("kappa"), w("kappa")) == {}
    assert A.bracket(w("kappa"), w("a_1_p"), 1, 1) == {}
    assert A.bracket(w("kappa"), w("b_1_p"), 1, 0) == {}
    # associativity spot check on a long word
    a, b, c = w("b_1_m", "a_1_m"), w("a_1_p", "b_1_p"), w("b_1_m", "b_1_p")
    assert A.mul(A.mul(a, b), c) == A.mul(a, A.mul(b, c))


# ---------------------------------------------------------------- basis and parity
@pytest.mark.parametrize("n", NS)
def test_basis_counts_and_parity(n):
    B = CBasis(n)
    d = dimension(n)
    assert len(B.even) == d["even"] == 2 * n * n + n + 1
    assert len(B.odd) == d["odd"] == 4 * n
    assert len(B.labels) == d["total"] == 2 * n * n + 5 * n + 1
    assert len(set(B.labels)) == len(B.labels)
    for lab in B.labels:
        assert B.parity[lab] == B.alg.element_parity(B.real[lab])
        assert B.parity[lab] == (1 if lab.startswith("E_eps1") else 0)
    assert B.labels == B.odd + B.even  # PBW: odd block before even block


def test_explicit_lists_n2():
    assert even_labels(2) == ["H_1", "H_2", "H_3", "E_2del1_p", "E_2del2_p", "E_del1_del2_pp",
                              "E_2del1_m", "E_2del2_m", "E_del1_del2_mm", "E_del1_del2_pm", "E_del1_del2_mp"]
    assert odd_labels(2) == ["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del2_pp", "E_eps1_del2_pm",
                             "E_eps1_del1_mp", "E_eps1_del1_mm", "E_eps1_del2_mp", "E_eps1_del2_mm"]


@pytest.mark.parametrize("n", NS)
def test_cartan_change_of_basis(n):
    """a_1^+ a_1^- = H_1 - sum_{k=2..n} H_k + H_{n+1} + K/2 ;
    b_k^+ b_k^- = sum_{l=k+1..n} H_l - H_{n+1} - K/2   (notation.md section 2)."""
    B = CBasis(n)
    w = B.word_to_basis
    exp = {"H_1": Fraction(1), f"H_{n+1}": Fraction(1), "K": Fraction(1, 2)}
    exp.update({f"H_{k}": Fraction(-1) for k in range(2, n + 1)})
    assert w[("a_1_p", "a_1_m")] == exp
    for k in range(1, n + 1):
        exp = {f"H_{l}": Fraction(1) for l in range(k + 1, n + 1)}
        exp[f"H_{n+1}"] = Fraction(-1)
        exp["K"] = Fraction(-1, 2)
        assert w[(f"b_{k}_p", f"b_{k}_m")] == exp
    assert w[()] == {"K": Fraction(1)}


# ---------------------------------------------------------------- structure constants
@pytest.mark.parametrize("n", NS)
def test_structure_constants_close_without_constants(n):
    B = CBasis(n)
    table, gamma = B.structure_constants()
    assert gamma == {}
    for (x, y), comps in table.items():
        assert "K" not in comps
        for z, c in comps.items():
            assert c.is_constant()
            assert B.parity[z] == (B.parity[x] + B.parity[y]) % 2


def test_hand_checked_brackets_n1():
    B = CBasis(1)
    t, _ = B.structure_constants()
    assert t[("E_eps1_del1_pm", "E_eps1_del1_mp")] == {"H_1": Poly.const(1)}
    assert t[("E_eps1_del1_pp", "E_eps1_del1_mm")] == {"H_1": Poly.const(-1), "H_2": Poly.const(-2)}
    assert t[("E_2del1_p", "E_2del1_m")] == {"H_2": Poly.const(4)}
    assert t[("H_1", "E_eps1_del1_pp")] == {"E_eps1_del1_pp": Poly.const(2)}
    assert ("H_1", "E_eps1_del1_pm") not in t          # isotropic root eps1-del1
    assert t[("H_2", "E_eps1_del1_pm")] == {"E_eps1_del1_pm": Poly.const(1)}
    assert t[("E_eps1_del1_pp", "E_eps1_del1_pp")] == {} if ("E_eps1_del1_pp", "E_eps1_del1_pp") in t else True


@pytest.mark.parametrize("n", NS)
def test_cartan_acts_diagonally(n):
    B = CBasis(n)
    t, _ = B.structure_constants()
    for h in [f"H_{k}" for k in range(1, n + 2)]:
        for lab in B.labels:
            comps = t.get((h, lab), {})
            assert set(comps) <= {lab}, (h, lab, comps)
            if lab.startswith("H_"):
                assert comps == {}


# ---------------------------------------------------------------- Schema 1 JSON
@pytest.mark.parametrize("n", NS)
def test_schema1_keys(n):
    d = build_schema1(n, date="2026-10-08")
    assert list(d) == ["schema_version", "algebra", "oscillator_generators", "oscillator_relations",
                       "central_elements", "basis", "parity", "generator_realization",
                       "structure_constants", "metadata"]
    a = d["algebra"]
    assert a["family"] == "C" and a["m"] == 1 and a["n"] == n and a["cartan_type"] == f"C({n+1})"
    assert a["dimension"]["formulas"] == {"even": "2n^2 + n + 1", "odd": "4n", "total": "2n^2 + 5n + 1"}
    assert a["dimension"]["even"] == 2 * n * n + n + 1 and a["dimension"]["odd"] == 4 * n
    og = d["oscillator_generators"]
    assert set(og) == {"fermions", "bosons"}
    assert og["fermions"]["m"] == 1 and og["fermions"]["labels"] == ["a_1_p", "a_1_m"]
    assert og["bosons"]["n"] == n and len(og["bosons"]["labels"]) == 2 * n
    assert "standard_fermion_anticommutators" in d["oscillator_relations"]
    assert "supplementary_fermion" not in json.dumps(og)
    ce = d["central_elements"]
    assert ce["kappa"]["parity"] == 1 and ce["K"]["parity"] == 0
    assert set(d["parity"]) == set(d["basis"]["even"]) | set(d["basis"]["odd"])
    assert d["basis"]["pbw_order"] == d["basis"]["odd"] + d["basis"]["even"]
    for e in d["structure_constants"]:
        assert set(e) == {"X", "Y", "Z", "coeff", "sign_rule"}
        assert e["Z"] in d["parity"]
        Fraction(e["coeff"])  # parses
    # every generator realization uses only a_1_± / b words
    for lab, r in d["generator_realization"]["realizations"].items():
        for term in r["standard_form"]:
            assert all(w.startswith(("a_1_", "b_")) for w in term["words"])
            assert "a_0" not in term["words"]


@pytest.mark.parametrize("n", NS)
def test_data_files_match_generator(n):
    path = os.path.join(DATA_DIR, f"C_{n}_structure.json")
    assert os.path.exists(path), "run python src/C_generators.py"
    with open(path) as fh:
        on_disk = json.load(fh)
    fresh = build_schema1(n, date=on_disk["metadata"]["generation_date"])
    assert on_disk == fresh
