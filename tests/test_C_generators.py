"""Unit tests for the C(n+1) Schema 1 generator (Issue I03)."""
import json
import os
import sys
from fractions import Fraction

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from C_generators import (build_elements, build_schema1, compute_structure_constants,  # noqa: E402
                          dimensions, even_labels, odd_labels, pbw_order)
from oscillator_algebra import Element, OscillatorAlgebra, graded_commutator  # noqa: E402

NS = [1, 2, 3]
REQUIRED_TOP_KEYS = ["schema_version", "schema_layer", "algebra", "oscillator_generators",
                     "oscillator_relations", "central_elements", "basis", "parity",
                     "generator_realization", "structure_constants", "metadata"]


@pytest.fixture(scope="module")
def schemas():
    return {n: build_schema1(n) for n in NS}


# --- engine sanity ---------------------------------------------------------
def test_engine_relations():
    alg = OscillatorAlgebra(2)
    ap, am = Element.word(alg, "a_1_p"), Element.word(alg, "a_1_m")
    assert (am * ap + ap * am) == Element.scalar(alg, 1)
    assert (ap * ap).is_zero() and (am * am).is_zero()
    b1p, b1m, b2p = Element.word(alg, "b_1_p"), Element.word(alg, "b_1_m"), Element.word(alg, "b_2_p")
    assert (b1m * b1p - b1p * b1m) == Element.scalar(alg, 1)
    assert (b1m * b2p - b2p * b1m).is_zero()
    assert graded_commutator(b1p, ap).is_zero()
    assert graded_commutator(ap, am) == Element.scalar(alg, 1)


# --- counts and labels -----------------------------------------------------
@pytest.mark.parametrize("n", NS)
def test_basis_counts(n):
    ev, od = even_labels(n), odd_labels(n)
    assert len(ev) == 2 * n * n + n + 1 == dimensions(n)["even"]
    assert len(od) == 4 * n == dimensions(n)["odd"]
    assert len(set(ev + od)) == len(ev) + len(od)
    assert pbw_order(n) == od + ev


def test_explicit_lists_match_notation():
    assert even_labels(1) == ["H_1", "H_2", "E_2del1_p", "E_2del1_m"]
    assert odd_labels(1) == ["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm"]
    assert even_labels(2) == ["H_1", "H_2", "H_3", "E_2del1_p", "E_2del2_p", "E_del1_del2_pp",
                              "E_2del1_m", "E_2del2_m", "E_del1_del2_mm", "E_del1_del2_pm", "E_del1_del2_mp"]
    assert odd_labels(3)[:3] == ["E_eps1_del1_pp", "E_eps1_del2_pp", "E_eps1_del3_pp"]
    assert len(even_labels(3)) == 22 and len(odd_labels(3)) == 12


# --- parity ----------------------------------------------------------------
@pytest.mark.parametrize("n", NS)
def test_parity_from_realization(n):
    alg = OscillatorAlgebra(n)
    els = build_elements(alg)
    for lab in even_labels(n):
        assert els[lab].parity() == 0
    for lab in odd_labels(n):
        assert els[lab].parity() == 1


@pytest.mark.parametrize("n", NS)
def test_schema_parity_and_realization_consistency(n, schemas):
    d = schemas[n]
    basis = d["basis"]["even"] + d["basis"]["odd"]
    assert set(d["parity"]) == set(basis)
    for lab in basis:
        r = d["generator_realization"]["realizations"][lab]
        assert r["parity"] == d["parity"][lab]
        for term in r["standard_form"]:
            nf = sum(1 for w in term["words"] if w.startswith("a_"))
            assert nf % 2 == d["parity"][lab]
    for lab in d["basis"]["even"]:
        assert d["parity"][lab] == 0
    for lab in d["basis"]["odd"]:
        assert d["parity"][lab] == 1


# --- structure constants --------------------------------------------------
@pytest.mark.parametrize("n", NS)
def test_closure_without_constant_terms(n):
    sc, _ = compute_structure_constants(n)  # raises if K appears
    labels = set(pbw_order(n))
    for e in sc:
        assert e["X"] in labels and e["Y"] in labels and e["Z"] in labels
        Fraction(e["coeff"])  # parses


@pytest.mark.parametrize("n", NS)
def test_cartan_commutes_and_weights(n, schemas):
    d = schemas[n]
    table = {}
    for e in d["structure_constants"]:
        table.setdefault((e["X"], e["Y"]), {})[e["Z"]] = Fraction(e["coeff"])
    H = [f"H_{k}" for k in range(1, n + 2)]
    for h1 in H:
        for h2 in H:
            assert (h1, h2) not in table
    # root vectors are weight vectors: [H, E] = c E
    for lab in pbw_order(n):
        if lab.startswith("H_"):
            continue
        for h in H:
            br = table.get((h, lab), {})
            assert set(br) <= {lab}


def test_specific_brackets_n1(schemas):
    d = schemas[1]
    table = {}
    for e in d["structure_constants"]:
        table.setdefault((e["X"], e["Y"]), {})[e["Z"]] = Fraction(e["coeff"])
    assert table[("E_2del1_p", "E_2del1_m")] == {"H_2": Fraction(4)}          # -4 N_1^s = 4 H_2
    assert table[("H_1", "E_eps1_del1_pp")] == {"E_eps1_del1_pp": Fraction(2)}
    assert table[("E_eps1_del1_pp", "E_eps1_del1_mm")] == {"H_1": Fraction(-1), "H_2": Fraction(-2)}
    assert ("E_eps1_del1_pp", "E_eps1_del1_pm") not in table  # same eps-sign anticommute


@pytest.mark.parametrize("n", NS)
def test_super_antisymmetry(n, schemas):
    d = schemas[n]
    p = d["parity"]
    table = {}
    for e in d["structure_constants"]:
        table.setdefault((e["X"], e["Y"]), {})[e["Z"]] = Fraction(e["coeff"])
    for (X, Y), br in table.items():
        sign = -1 if (p[X] and p[Y]) else 1
        rev = table.get((Y, X), {})
        assert rev == {Z: -sign * c for Z, c in br.items()}


@pytest.mark.parametrize("n", [1, 2])
def test_super_jacobi_small(n, schemas):
    d = schemas[n]
    p = d["parity"]
    labels = d["basis"]["pbw_order"]
    table = {}
    for e in d["structure_constants"]:
        table.setdefault((e["X"], e["Y"]), {})[e["Z"]] = Fraction(e["coeff"])

    def br(X, Y):
        return table.get((X, Y), {})

    def br_el(X, vec):
        out = {}
        for W, c in vec.items():
            for Z, cz in br(X, W).items():
                out[Z] = out.get(Z, 0) + c * cz
        return {k: v for k, v in out.items() if v != 0}

    for X in labels:
        for Y in labels:
            for Z in labels:
                total = {}
                for (A, B, C) in ((X, Y, Z), (Y, Z, X), (Z, X, Y)):
                    sign = -1 if (p[A] * p[C]) % 2 else 1
                    for W, c in br_el(A, br(B, C)).items():
                        total[W] = total.get(W, 0) + sign * c
                assert all(v == 0 for v in total.values()), (X, Y, Z, total)


# --- schema conformance -----------------------------------------------------
@pytest.mark.parametrize("n", NS)
def test_schema_conformance(n, schemas):
    d = schemas[n]
    for k in REQUIRED_TOP_KEYS:
        assert k in d
    a = d["algebra"]
    assert a["family"] == "C" and a["m"] == 1 and a["n"] == n
    assert a["cartan_type"] == f"C({n+1})"
    assert a["dimension"]["formulas"] == {"even": "2n^2 + n + 1", "odd": "4n", "total": "2n^2 + 5n + 1"}
    assert a["dimension"]["even"] == len(d["basis"]["even"])
    assert a["dimension"]["odd"] == len(d["basis"]["odd"])
    og = d["oscillator_generators"]
    assert set(og) == {"fermions", "bosons"}
    assert og["fermions"]["m"] == 1 and og["fermions"]["labels"] == ["a_1_p", "a_1_m"]
    assert og["bosons"]["n"] == n and len(og["bosons"]["labels"]) == 2 * n
    ce = d["central_elements"]
    assert ce["kappa"]["parity"] == 1 and ce["K"]["parity"] == 0
    assert "standard_fermion_anticommutators" in d["oscillator_relations"]
    assert d["basis"]["ordering_convention"].startswith("PBW: kappa < [odd] < [even]")
    assert d["structure_constants_convention"]["count"] == len(d["structure_constants"])


@pytest.mark.parametrize("n", NS)
def test_data_files_match_generator(n, schemas):
    path = os.path.join(ROOT, "data", f"C_{n}_structure.json")
    assert os.path.exists(path), "run python3 src/C_generators.py"
    on_disk = json.load(open(path))
    fresh = schemas[n]
    for k in REQUIRED_TOP_KEYS:
        if k == "metadata":
            continue
        assert on_disk[k] == fresh[k], k
