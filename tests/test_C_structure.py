"""Unit tests for Schema 1 of C(n+1) = osp(2|2n) (Issue I03)."""
import json
import os
import sys
from fractions import Fraction

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from C_generators import CAlgebra, build_schema1, dimension, even_basis, odd_basis, pbw_order  # noqa: E402
from osc_algebra import OscillatorAlgebra, Poly, el_from_words  # noqa: E402

NS = [1, 2, 3]


def load(n):
    with open(os.path.join(ROOT, "data", f"C_{n}_structure.json"), encoding="utf-8") as fh:
        return json.load(fh)


def table(doc):
    """{(X,Y): {Z: Fraction}} from the JSON records."""
    t = {}
    for r in doc["structure_constants"]:
        t.setdefault((r["X"], r["Y"]), {})[r["Z"]] = Fraction(r["coeff"])
    return t


# ----------------------------------------------------------------- oscillator engine


def test_engine_ccr_car():
    A = OscillatorAlgebra(2)
    assert A.normal_order(("b_1_m", "b_1_p")) == {("b_1_p", "b_1_m"): Poly.const(1), (): Poly.const(1)}
    assert A.normal_order(("b_2_m", "b_1_p")) == {("b_1_p", "b_2_m"): Poly.const(1)}
    assert A.normal_order(("a_1_m", "a_1_p")) == {("a_1_p", "a_1_m"): Poly.const(-1), (): Poly.const(1)}
    assert A.normal_order(("a_1_p", "a_1_p")) == {}
    assert A.normal_order(("b_1_p", "a_1_p")) == {("a_1_p", "b_1_p"): Poly.const(1)}


def test_engine_kappa_rules():
    A = OscillatorAlgebra(1, deformation="symbolic")
    # b_1^+ a_1^- = a_1^- b_1^+ - gb_a1m_b1p kappa
    res = A.normal_order(("b_1_p", "a_1_m"))
    assert res[("a_1_m", "b_1_p")] == Poly.const(1)
    assert res[("kappa",)] == Poly.symbol("gb_a1m_b1p", -1)
    # kappa anticommutes with odd, commutes with even, squares to zero
    assert A.normal_order(("a_1_p", "kappa")) == {("kappa", "a_1_p"): Poly.const(-1)}
    assert A.normal_order(("b_1_p", "kappa")) == {("kappa", "b_1_p"): Poly.const(1)}
    assert A.normal_order(("kappa", "kappa")) == {}


# ----------------------------------------------------------------- basis / counts


@pytest.mark.parametrize("n", NS)
def test_dimension_formulas(n):
    d = dimension(n)
    assert d["even"] == 2 * n * n + n + 1 and d["odd"] == 4 * n
    assert len(even_basis(n)) == d["even"] and len(odd_basis(n)) == d["odd"]
    assert {1: (4, 4), 2: (11, 8), 3: (22, 12)}[n] == (d["even"], d["odd"])


@pytest.mark.parametrize("n", NS)
def test_labels_unique_and_ordered(n):
    labs = pbw_order(n)
    assert len(set(labs)) == len(labs)
    assert labs == odd_basis(n) + even_basis(n)
    assert all(l.startswith("E_eps1_") for l in odd_basis(n))
    assert not any(l.startswith("E_eps1_") for l in even_basis(n))


def test_explicit_lists_match_notation():
    assert even_basis(1) == ["H_1", "H_2", "E_2del1_p", "E_2del1_m"]
    assert odd_basis(1) == ["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm"]
    assert even_basis(2) == ["H_1", "H_2", "H_3", "E_2del1_p", "E_2del2_p", "E_del1_del2_pp",
                             "E_2del1_m", "E_2del2_m", "E_del1_del2_mm", "E_del1_del2_pm", "E_del1_del2_mp"]


# ----------------------------------------------------------------- JSON conformance


@pytest.mark.parametrize("n", NS)
def test_json_top_level_and_algebra(n):
    doc = load(n)
    expected = {"schema_version", "algebra", "oscillator_generators", "oscillator_relations",
                "central_elements", "basis", "parity", "generator_realization",
                "structure_constants", "metadata"}
    assert set(doc) == expected
    a = doc["algebra"]
    assert a["family"] == "C" and a["m"] == 1 and a["n"] == n
    assert a["cartan_type"] == f"C({n+1})" and a["alternative_notation"]["osp"] == f"osp(2|{2*n})"
    assert a["dimension_formula"] == {"even": "2n^2 + n + 1", "odd": "4n", "total": "2n^2 + 5n + 1"}
    assert a["dimension"] == dimension(n)
    og = doc["oscillator_generators"]
    assert set(og) == {"fermions", "bosons"}
    assert og["fermions"]["labels"] == ["a_1_p", "a_1_m"] and og["fermions"]["m"] == 1
    assert og["bosons"]["n"] == n and len(og["bosons"]["labels"]) == 2 * n
    ce = doc["central_elements"]
    assert ce["kappa"]["parity"] == 1 and ce["K"]["parity"] == 0
    assert "standard_fermion_anticommutators" in doc["oscillator_relations"]
    assert "supplementary_fermion_relation" not in doc["oscillator_relations"]


@pytest.mark.parametrize("n", NS)
def test_json_basis_parity_realization(n):
    doc = load(n)
    b = doc["basis"]
    assert b["even"] == even_basis(n) and b["odd"] == odd_basis(n)
    assert b["pbw_order"] == odd_basis(n) + even_basis(n)
    assert b["cartan"] == [f"H_{k}" for k in range(1, n + 2)]
    par = doc["parity"]
    assert set(par) == set(b["even"]) | set(b["odd"])
    assert all(par[l] == 0 for l in b["even"]) and all(par[l] == 1 for l in b["odd"])
    og = doc["oscillator_generators"]
    allowed = set(og["fermions"]["labels"]) | set(og["bosons"]["labels"])
    order = doc["generator_realization"]["ordering"].split(", ")
    pos = {s: i for i, s in enumerate(order)}
    A = OscillatorAlgebra(n)
    for lab, entry in doc["generator_realization"]["realizations"].items():
        assert entry["parity"] == par[lab]
        for term in entry["standard_form"]:
            words = term["words"]
            assert set(words) <= allowed
            assert words == sorted(words, key=lambda s: pos[s])          # normal ordered
            assert sum(A.parity[w] for w in words) % 2 == par[lab]         # realization parity
            assert "a_0" not in words
            Fraction(term["coeff"])                                        # parses


@pytest.mark.parametrize("n", NS)
def test_data_files_are_current(n):
    doc = load(n)
    fresh = build_schema1(n, today=doc["metadata"]["generation_date"])
    assert fresh == doc


# ----------------------------------------------------------------- algebraic properties


@pytest.mark.parametrize("n", NS)
def test_closure_parity_and_antisymmetry(n):
    doc = load(n)
    par = doc["parity"]
    t = table(doc)
    labs = pbw_order(n)
    for (x, y), comps in t.items():
        for z, c in comps.items():
            assert z in par, f"non-basis target {z} in [{x},{y}]"
            assert par[z] == (par[x] + par[y]) % 2
    for x in labs:
        for y in labs:
            xy = t.get((x, y), {})
            yx = t.get((y, x), {})
            sign = -1 if (par[x] == 1 and par[y] == 1) else 1
            for z in set(xy) | set(yx):
                assert yx.get(z, 0) == -sign * xy.get(z, 0), (x, y, z)


@pytest.mark.parametrize("n", NS)
def test_cartan_abelian_and_root_vectors(n):
    doc = load(n)
    t = table(doc)
    roots = {l: e["root"] for l, e in doc["generator_realization"]["realizations"].items()}
    cartan = doc["basis"]["cartan"]
    for h1 in cartan:
        for h2 in cartan:
            assert (h1, h2) not in t
    for h in cartan:
        for e, r in roots.items():
            if r is None:
                continue
            comps = t.get((h, e), {})
            assert set(comps) <= {e}, f"[{h},{e}] not proportional to {e}"
    # root additivity: [E_a, E_b] lands on root a+b (or in Cartan if a+b = 0)
    for (x, y), comps in t.items():
        rx, ry = roots[x], roots[y]
        if rx is None or ry is None:
            continue
        s = (rx["eps"] + ry["eps"], [u + v for u, v in zip(rx["delta"], ry["delta"])])
        for z in comps:
            rz = roots[z]
            if rz is None:
                assert s == (0, [0] * n)
            else:
                assert (rz["eps"], rz["delta"]) == s


@pytest.mark.parametrize("n", NS)
def test_count_nonzero_pairs_and_chevalley_relations(n):
    doc = load(n)
    t = table(doc)
    # Chevalley-type relations from Cn1_definition.md
    assert t[("E_eps1_del1_pm", "E_eps1_del1_mp")] == {"H_1": Fraction(1)}
    for k in range(2, n + 1):
        assert t[(f"E_del{k-1}_del{k}_pm", f"E_del{k-1}_del{k}_mp")] == {f"H_{k}": Fraction(1)}
    # [E_{2δ_n}, E_{-2δ_n}] = 4 H_{n+1}  (because H_{n+1} = [E/2, E/2])
    assert t[(f"E_2del{n}_p", f"E_2del{n}_m")] == {f"H_{n+1}": Fraction(4)}
    # every odd generator squares to zero
    for o in odd_basis(n):
        assert (o, o) not in t


def test_hand_computed_n1():
    t = table(load(1))
    assert t[("E_eps1_del1_pp", "E_eps1_del1_mm")] == {"H_1": Fraction(-1), "H_2": Fraction(-2)}
    assert t[("H_1", "E_eps1_del1_pp")] == {"E_eps1_del1_pp": Fraction(2)}
    assert ("H_1", "E_eps1_del1_pm") not in t          # (ε-δ_1)(H_1) = 0
    assert t[("H_2", "E_2del1_p")] == {"E_2del1_p": Fraction(-2)}
    assert t[("E_2del1_m", "E_eps1_del1_pp")] == {"E_eps1_del1_pm": Fraction(2)}


def test_calgebra_bracket_matches_engine_directly():
    C = CAlgebra(2)
    z0, z1 = C.bracket("E_del1_del2_pm", "E_del1_del2_mp")
    assert z1 == {} and z0 == {"H_2": Poly.const(1)}
    # [b_1^+ b_2^+, b_1^- b_2^-] = -(b_1^+b_1^- + b_2^+b_2^- + 1) = -(H_2 + H_3 - H_3) - ... check via engine
    z0, _ = C.bracket("E_del1_del2_pp", "E_del1_del2_mm")
    target = el_from_words([(("b_1_p", "b_1_m"), -1), (("b_2_p", "b_2_m"), -1), ((), -1)])
    assert C.decomposer.decompose(target) == z0
