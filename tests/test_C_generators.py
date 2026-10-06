import json
import os
from fractions import Fraction

import pytest

from conftest import DATA
from C_generators import build_schema1, even_basis, make_algebra, odd_basis
from C_oscillator import Oscillators, lin

NS = [1, 2, 3]


@pytest.mark.parametrize("n", NS)
def test_generator_counts(n):
    assert len(even_basis(n)) == 2 * n * n + n + 1
    assert len(odd_basis(n)) == 4 * n
    assert len(set(even_basis(n) + odd_basis(n))) == 2 * n * n + 5 * n + 1


@pytest.mark.parametrize("n", NS)
def test_parity_from_realization(n):
    alg = make_algebra(n)
    for x in alg.basis:
        for (k, w), _ in alg.gen[x].items():
            if w:
                assert alg.osc.word_parity(w) == alg.parity[x], x
    assert all(alg.parity[x] == 1 for x in odd_basis(n))
    assert all(alg.parity[x] == 0 for x in even_basis(n))


def test_oscillator_relations():
    osc = Oscillators(2)
    ap, am, b1p, b1m = (osc.index[l] for l in ["a_1_p", "a_1_m", "b_1_p", "b_1_m"])
    # a- a+ = 1 - a+ a-
    assert osc.normal_order((am, ap)) == {(0, ()): lin(1), (0, (ap, am)): lin(-1)}
    assert osc.normal_order((ap, ap)) == {}
    # b- b+ = b+ b- + 1
    assert osc.normal_order((b1m, b1p)) == {(0, (b1p, b1m)): lin(1), (0, ()): lin(1)}
    # b a = a b (undeformed)
    assert osc.normal_order((b1p, ap)) == {(0, (ap, b1p)): lin(1)}


def test_deformed_relation():
    osc = Oscillators(1, deformed=True)
    ap, b1m = osc.index["a_1_p"], osc.index["b_1_m"]
    # b a = a b + [b, a] = a b - gb kappa
    assert osc.normal_order((b1m, ap)) == {(0, (ap, b1m)): lin(1), (1, ()): lin(-1, "gb_a1p_b1m")}


@pytest.mark.parametrize("n", NS)
def test_schema1_file_consistency(n):
    path = os.path.join(DATA, f"C_{n}_structure.json")
    with open(path) as fh:
        d = json.load(fh)
    fresh = build_schema1(n)
    d["metadata"].pop("generation_date")
    fresh["metadata"].pop("generation_date")
    assert d == fresh
    assert d["algebra"]["m"] == 1 and d["algebra"]["family"] == "C"
    assert d["central_elements"]["kappa"]["parity"] == 1
    assert d["central_elements"]["K"]["parity"] == 0
    assert set(d["oscillator_generators"]) == {"fermions", "bosons"}
    basis = d["basis"]["odd"] + d["basis"]["even"]
    assert set(d["parity"]) == set(basis) == set(d["generator_realization"]["realizations"])
    for e in d["structure_constants"]:
        assert e["X"] in basis and e["Y"] in basis and e["Z"] in basis
        # parity of bracket = p(X) + p(Y)
        assert d["parity"][e["Z"]] == (d["parity"][e["X"]] + d["parity"][e["Y"]]) % 2


@pytest.mark.parametrize("n", NS)
def test_graded_antisymmetry(n):
    with open(os.path.join(DATA, f"C_{n}_structure.json")) as fh:
        d = json.load(fh)
    sc = {(e["X"], e["Y"], e["Z"]): Fraction(e["coeff"]) for e in d["structure_constants"]}
    p = d["parity"]
    for (x, y, z), c in sc.items():
        assert sc.get((y, x, z), 0) == -(-1) ** (p[x] * p[y]) * c


def test_known_brackets_n1():
    alg = make_algebra(1)

    def br(x, y):
        return {z: v["1"] for z, v in alg.decompose(alg.bracket_labels(x, y)).get(0, {}).items()}

    assert br("E_eps1_del1_pp", "E_eps1_del1_mm") == {"H_1": -1, "H_2": -2}
    assert br("E_eps1_del1_pm", "E_eps1_del1_mp") == {"H_1": 1}
    assert br("E_2del1_p", "E_2del1_m") == {"H_2": 4}
    assert br("H_1", "E_eps1_del1_pp") == {"E_eps1_del1_pp": 2}
