import json
import os
from fractions import Fraction

import pytest

from C_generators import DATA_DIR, CAlgebra, build_basis, build_schema1
from oscillator import OscillatorAlgebra

NS = [1, 2, 3]


def test_oscillator_relations():
    A = OscillatorAlgebra(1)
    e = lambda *w: {(0, None, tuple(w)): Fraction(1)}  # noqa: E731
    # a^- a^+ = 1 - a^+ a^-
    assert A.normal_order(e("a_1_m", "a_1_p")) == {(0, None, ()): 1, (0, None, ("a_1_p", "a_1_m")): -1}
    # b^- b^+ = b^+ b^- + 1
    assert A.normal_order(e("b_1_m", "b_1_p")) == {(0, None, ()): 1, (0, None, ("b_1_p", "b_1_m")): 1}
    assert A.normal_order(e("a_1_p", "a_1_p")) == {}
    # undeformed: b a = a b
    assert A.normal_order(e("b_1_p", "a_1_m")) == {(0, None, ("a_1_m", "b_1_p")): 1}
    D = OscillatorAlgebra(1, deformed=True)
    # deformed: b a = a b - gb kappa
    assert D.normal_order(e("b_1_p", "a_1_m")) == {(0, None, ("a_1_m", "b_1_p")): 1,
                                                   (1, "gb_m_1_p", ()): -1}


@pytest.mark.parametrize("n", NS)
def test_counts_and_parity(n):
    even, odd = build_basis(n)
    assert len(even) == 2 * n * n + n + 1
    assert len(odd) == 4 * n
    assert len(set(even + odd)) == len(even) + len(odd)
    C = CAlgebra(n)
    assert all(C.parity[x] == 0 for x in even)
    assert all(C.parity[x] == 1 for x in odd)
    # realization parity = parity of oscillator words
    for lab in C.basis:
        for (_, _, w) in C.elem[lab]:
            assert sum(x.startswith("a_") for x in w) % 2 == C.parity[lab]


@pytest.mark.parametrize("n", NS)
def test_bracket_parity_and_closure(n):
    data = build_schema1(n)
    par = data["parity"]
    for e in data["structure_constants"]:
        assert par[e["Z"]] == (par[e["X"]] + par[e["Y"]]) % 2
    # Chevalley-type checks
    sc = {(e["X"], e["Y"], e["Z"]): Fraction(e["coeff"]) for e in data["structure_constants"]}
    assert sc[(f"E_2del{n}_p", f"E_2del{n}_m", f"H_{n+1}")] == 1
    assert sc[("E_eps1_del1_pm", "E_eps1_del1_mp", "H_1")] == 1


@pytest.mark.parametrize("n", NS)
def test_json_matches_generator(n):
    path = os.path.join(DATA_DIR, f"C_{n}_structure.json")
    with open(path) as f:
        on_disk = json.load(f)
    fresh = build_schema1(n)
    assert on_disk["structure_constants"] == fresh["structure_constants"]
    assert on_disk["basis"] == fresh["basis"]
    alg = on_disk["algebra"]
    assert alg["family"] == "C" and alg["m"] == 1 and alg["n"] == n
    assert alg["dimension"] == {"total": 2 * n * n + 5 * n + 1, "even": 2 * n * n + n + 1, "odd": 4 * n}
    assert set(on_disk["central_elements"]) == {"kappa", "K"}
    assert on_disk["central_elements"]["kappa"]["parity"] == 1
    assert on_disk["central_elements"]["K"]["parity"] == 0
    assert set(on_disk["oscillator_generators"]) == {"fermions", "bosons"}
    # every label used in structure constants is a basis element
    basis = set(on_disk["basis"]["even"]) | set(on_disk["basis"]["odd"])
    for e in on_disk["structure_constants"]:
        assert {e["X"], e["Y"], e["Z"]} <= basis
