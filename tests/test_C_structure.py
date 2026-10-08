"""Unit tests for I03: C(n+1) basis, oscillator engine and Schema 1 JSON."""
import json
import os
import sys
from fractions import Fraction

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from C_generators import (build_structure_json, even_labels, odd_labels, pbw_order,  # noqa: E402
                          parity_of, realization_words, compute_brackets)
from oscillator import Element, LinPoly, OscillatorAlgebra  # noqa: E402

NS = [1, 2, 3]


@pytest.fixture(scope="module")
def schemas():
    return {n: build_structure_json(n) for n in NS}


# ---------------------------------------------------------------- oscillator engine
def test_car_ccr_relations():
    alg = OscillatorAlgebra(2)
    ap, am = Element.word(alg, "a_1_p"), Element.word(alg, "a_1_m")
    assert (am * ap + ap * am).terms == Element.scalar(alg, 1).terms
    assert (ap * ap).is_zero() and (am * am).is_zero()
    b1p, b1m, b2p = Element.word(alg, "b_1_p"), Element.word(alg, "b_1_m"), Element.word(alg, "b_2_p")
    assert (b1m * b1p - b1p * b1m).terms == Element.scalar(alg, 1).terms
    assert (b1m * b2p - b2p * b1m).is_zero()
    assert (b1p * am - am * b1p).is_zero()           # undeformed: bosons and fermions commute


def test_deformed_relation_and_kappa_nilpotent():
    alg = OscillatorAlgebra(1, deformed=True)
    ap, b1p = Element.word(alg, "a_1_p"), Element.word(alg, "b_1_p")
    comm = b1p * ap - ap * b1p
    assert comm.terms == {("kappa",): -LinPoly.symbol("gb_a_1_p_b_1_p")}
    k = Element.word(alg, "kappa")
    assert (k * k).is_zero()
    # supercentral: kappa a = - a kappa, kappa b = b kappa
    assert (k * ap + ap * k).is_zero()
    assert (k * b1p - b1p * k).is_zero()


# ---------------------------------------------------------------- basis
@pytest.mark.parametrize("n", NS)
def test_dimensions(n):
    assert len(even_labels(n)) == 2 * n * n + n + 1
    assert len(odd_labels(n)) == 4 * n
    assert len(set(pbw_order(n))) == 2 * n * n + 5 * n + 1


def test_explicit_lists_match_notation():
    assert even_labels(1) == ["H_1", "H_2", "E_2del1_p", "E_2del1_m"]
    assert odd_labels(1) == ["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm"]
    assert even_labels(2) == ["H_1", "H_2", "H_3", "E_2del1_p", "E_2del2_p", "E_del1_del2_pp",
                              "E_2del1_m", "E_2del2_m", "E_del1_del2_mm", "E_del1_del2_pm", "E_del1_del2_mp"]
    assert odd_labels(2) == ["E_eps1_del1_pp", "E_eps1_del2_pp", "E_eps1_del1_pm", "E_eps1_del2_pm",
                             "E_eps1_del1_mp", "E_eps1_del2_mp", "E_eps1_del1_mm", "E_eps1_del2_mm"]


@pytest.mark.parametrize("n", NS)
def test_parity_consistent_with_realization(n):
    alg = OscillatorAlgebra(n)
    for lab in pbw_order(n):
        words, _, _ = realization_words(n, lab)
        e = Element(alg, {w: LinPoly(c) for w, c in words})
        assert e.parity() == parity_of(lab)


# ---------------------------------------------------------------- structure constants
@pytest.mark.parametrize("n", NS)
def test_brackets_close_without_constants(n):
    # compute_brackets raises if any bracket has a constant part or leaves the span
    _, _, _, table = compute_brackets(n)
    assert len(table) == len(pbw_order(n)) ** 2


@pytest.mark.parametrize("n", NS)
def test_cartan_eigenvalues_equal_roots(n):
    """[H_i, E_alpha] = alpha(H_i) E_alpha with alpha(H_i) read off from the root vector:
    H_1 = N_a + N_1 ~ eps + del_1, H_k ~ del_{k-1} - del_k, H_{n+1} ~ -del_n."""
    _, _, _, table = compute_brackets(n)
    for lab in pbw_order(n):
        _, _, vec = realization_words(n, lab)
        if vec is None:
            continue
        for i in range(1, n + 2):
            if i == 1:
                ev = vec[0] + vec[1]
            elif i <= n:
                ev = vec[i - 1] - vec[i]
            else:
                ev = -vec[n]
            c0, _, _ = table[(f"H_{i}", lab)]
            got = {z: c.scalar_value() for z, c in c0.items()}
            expected = {lab: Fraction(ev)} if ev != 0 else {}
            assert got == expected, (f"H_{i}", lab, got, expected)


@pytest.mark.parametrize("n", NS)
def test_bracket_parity_grading(n):
    _, _, _, table = compute_brackets(n)
    for (x, y), (c0, _, _) in table.items():
        for z in c0:
            assert parity_of(z) == (parity_of(x) + parity_of(y)) % 2


def test_hand_computed_n1_values():
    _, _, _, table = compute_brackets(1)

    def br(x, y):
        return {z: c.scalar_value() for z, c in table[(x, y)][0].items()}

    assert br("E_2del1_p", "E_2del1_m") == {"H_2": Fraction(4)}
    assert br("E_eps1_del1_pm", "E_eps1_del1_mp") == {"H_1": Fraction(1)}
    assert br("E_eps1_del1_pp", "E_eps1_del1_mm") == {"H_1": Fraction(-1), "H_2": Fraction(-2)}
    assert br("H_1", "E_eps1_del1_pp") == {"E_eps1_del1_pp": Fraction(2)}
    assert br("E_eps1_del1_pp", "E_eps1_del1_pp") == {}


# ---------------------------------------------------------------- Schema 1 JSON conformance
@pytest.mark.parametrize("n", NS)
def test_schema1_top_level_and_algebra(schemas, n):
    d = schemas[n]
    assert set(d) == {"schema_version", "algebra", "oscillator_generators", "oscillator_relations",
                      "central_elements", "basis", "parity", "generator_realization",
                      "structure_constants", "metadata"}
    a = d["algebra"]
    assert a["family"] == "C" and a["m"] == 1 and a["n"] == n and a["cartan_type"] == f"C({n+1})"
    assert a["dimension_formula"] == {"even": "2n^2 + n + 1", "odd": "4n", "total": "2n^2 + 5n + 1"}
    assert a["dimension"] == {"even": 2 * n * n + n + 1, "odd": 4 * n, "total": 2 * n * n + 5 * n + 1}
    og = d["oscillator_generators"]
    assert set(og) == {"fermions", "bosons"}
    assert og["fermions"]["labels"] == ["a_1_p", "a_1_m"] and og["fermions"]["m"] == 1
    assert og["bosons"]["n"] == n and len(og["bosons"]["labels"]) == 2 * n
    assert d["central_elements"]["kappa"]["parity"] == 1 and d["central_elements"]["K"]["parity"] == 0
    assert "standard_fermion_anticommutators" in d["oscillator_relations"]
    assert "supplementary_fermion" not in og


@pytest.mark.parametrize("n", NS)
def test_schema1_basis_parity_realization(schemas, n):
    d = schemas[n]
    assert d["basis"]["even"] == even_labels(n) and d["basis"]["odd"] == odd_labels(n)
    assert d["basis"]["pbw_order"] == odd_labels(n) + even_labels(n)
    assert all(d["parity"][l] == 1 for l in d["basis"]["odd"])
    assert all(d["parity"][l] == 0 for l in d["basis"]["even"])
    real = d["generator_realization"]["realizations"]
    assert set(real) == set(d["basis"]["pbw_order"])
    for lab, r in real.items():
        assert r["parity"] == d["parity"][lab]
        for term in r["standard_form"]:
            Fraction(term["coeff"])  # parses as exact rational
            for w in term["words"]:
                assert w.startswith(("a_1_", "b_"))
                assert "a_0" not in w


@pytest.mark.parametrize("n", NS)
def test_schema1_structure_constants_conform(schemas, n):
    d = schemas[n]
    labels = set(d["basis"]["pbw_order"])
    seen = set()
    for e in d["structure_constants"]:
        assert set(e) == {"X", "Y", "Z", "coeff", "sign_rule"}
        assert e["X"] in labels and e["Y"] in labels and e["Z"] in labels
        assert e["sign_rule"] == "graded"
        assert Fraction(e["coeff"]) != 0
        key = (e["X"], e["Y"], e["Z"])
        assert key not in seen
        seen.add(key)
        assert d["parity"][e["Z"]] == (d["parity"][e["X"]] + d["parity"][e["Y"]]) % 2


@pytest.mark.parametrize("n", NS)
def test_data_files_match_generator(n):
    path = os.path.join(ROOT, "data", f"C_{n}_structure.json")
    assert os.path.exists(path), "run python src/C_generators.py"
    on_disk = json.load(open(path))
    fresh = build_structure_json(n)
    on_disk["metadata"].pop("generation_date")
    fresh["metadata"].pop("generation_date")
    assert on_disk == fresh
