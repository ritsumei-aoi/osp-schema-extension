import json
import os
import sys
from fractions import Fraction

import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))

import C_generators as G  # noqa: E402

NS = [1, 2, 3]
TOP_KEYS = ["schema_version", "algebra", "oscillator_generators", "oscillator_relations",
            "central_elements", "basis", "parity", "generator_realization",
            "structure_constants", "metadata"]


def load(n):
    with open(os.path.join(ROOT, "data", f"C_{n}_structure.json")) as f:
        return json.load(f)


@pytest.mark.parametrize("n", NS)
def test_generator_counts(n):
    assert len(G.even_names(n)) == 2 * n * n + n + 1
    assert len(G.odd_names(n)) == 4 * n
    assert len(set(G.basis_names(n))) == 2 * n * n + 5 * n + 1


@pytest.mark.parametrize("n", NS)
def test_parity_labels(n):
    for nm in G.odd_names(n):
        assert G.parity_of(nm) == 1
    for nm in G.even_names(n):
        assert G.parity_of(nm) == 0


@pytest.mark.parametrize("n", NS)
def test_realization_parity_matches_fermion_number(n):
    for nm in G.basis_names(n):
        for w in G.realization(nm, n):
            assert sum(l.startswith("a_") for l in w) % 2 == G.parity_of(nm)


@pytest.mark.parametrize("n", NS)
def test_schema_keys_and_algebra_field(n):
    d = load(n)
    assert list(d) == TOP_KEYS
    a = d["algebra"]
    assert a["family"] == "C" and a["m"] == 1 and a["n"] == n
    assert a["dimension"] == {"total": 2 * n * n + 5 * n + 1, "even": 2 * n * n + n + 1,
                              "odd": 4 * n}
    assert set(d["oscillator_generators"]) == {"fermions", "bosons"}
    assert d["oscillator_generators"]["fermions"]["labels"] == ["a_1_p", "a_1_m"]
    assert len(d["oscillator_generators"]["bosons"]["labels"]) == 2 * n
    ce = d["central_elements"]
    assert ce["kappa"]["parity"] == 1 and ce["K"]["parity"] == 0
    assert d["basis"]["even"] == G.even_names(n) and d["basis"]["odd"] == G.odd_names(n)
    assert set(d["parity"]) == set(G.basis_names(n))


@pytest.mark.parametrize("n", NS)
def test_structure_constants_parity_and_antisymmetry(n):
    d = load(n)
    par = d["parity"]
    table = {}
    for e in d["structure_constants"]:
        assert par[e["Z"]] == (par[e["X"]] + par[e["Y"]]) % 2
        table[(e["X"], e["Y"], e["Z"])] = Fraction(e["coeff"])
    for (X, Y, Z), c in table.items():
        sgn = -1 if par[X] * par[Y] == 0 else 1  # [Y,X} = -(-1)^{xy} [X,Y}
        assert table.get((Y, X, Z)) == sgn * c


@pytest.mark.parametrize("n", NS)
def test_file_matches_regeneration(n):
    assert G.build_schema1(n)["structure_constants"] == load(n)["structure_constants"]


def test_known_brackets_n1():
    sc = {(e["X"], e["Y"], e["Z"]): Fraction(e["coeff"]) for e in load(1)["structure_constants"]}
    # [b^-^2, b^+^2] = 4 b+b- + 2 => [E_p, E_m] = -(4N+2) = 4 H_2
    assert sc[("E_2del1_p", "E_2del1_m", "H_2")] == 4
    # {a+ b-, a- b+} = N_a + N_b = H_1 (computed by hand in the I03 log)
    assert sc[("E_eps1_del1_pm", "E_eps1_del1_mp", "H_1")] == 1
    # same-fermion odd generators anticommute to zero
    assert not any(k[0] == "E_eps1_del1_pp" and k[1] == "E_eps1_del1_pm" for k in sc)


def test_expander_rejects_outside_span():
    ex = G.BasisExpander(1)
    with pytest.raises(ValueError):
        ex.expand({("a_1_p",): Fraction(1)})
