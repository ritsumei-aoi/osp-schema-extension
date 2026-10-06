"""Tests for Schema 1 (Issue I03)."""
import json
import os
from fractions import Fraction

import pytest

from conftest import DATA
from C_generators import (build_schema1, even_basis, odd_basis, realizations, global_order,
                          parity_map)
from oscillator_algebra import OscillatorAlgebra

NS = (1, 2, 3)


def load(n):
    with open(os.path.join(DATA, f"C_{n}_structure.json")) as f:
        return json.load(f)


@pytest.mark.parametrize("n", NS)
def test_generator_counts(n):
    assert len(even_basis(n)) == 2 * n * n + n + 1
    assert len(odd_basis(n)) == 4 * n
    assert len(set(global_order(n))) == 2 * n * n + 5 * n + 1


@pytest.mark.parametrize("n", NS)
def test_parity_matches_oscillator_words(n):
    alg = OscillatorAlgebra(n)
    par = parity_map(n)
    for lab, e in realizations(n, alg).items():
        assert alg.parity(e) == par[lab], lab
        assert par[lab] == (1 if lab.startswith("E_eps1") else 0)


def test_oscillator_relations():
    alg = OscillatorAlgebra(1)
    a_p, a_m, b_p, b_m = ({(x,): Fraction(1)} for x in ("a_1_p", "a_1_m", "b_1_p", "b_1_m"))
    assert alg.bracket(a_m, a_p) == {(): 1}
    assert alg.bracket(a_p, a_p) == {}
    assert alg.bracket(b_m, b_p) == {(): 1}
    assert alg.bracket(b_p, a_p) == {}
    dalg = OscillatorAlgebra(1, gb={"gb_p_1_m": 3})
    assert dalg.bracket(b_m, a_p) == {("kappa",): -3}
    assert dalg.bracket(a_p, b_m) == {("kappa",): 3}


@pytest.mark.parametrize("n", NS)
def test_json_matches_spec_and_generator(n):
    d = load(n)
    assert d["schema_version"] == "5.0"
    assert set(d) == {"schema_version", "algebra", "oscillator_generators", "oscillator_relations",
                      "central_elements", "basis", "parity", "generator_realization",
                      "structure_constants", "metadata"}
    alg = d["algebra"]
    assert (alg["family"], alg["m"], alg["n"]) == ("C", 1, n)
    assert alg["dimension"] == {"total": 2 * n * n + 5 * n + 1, "even": 2 * n * n + n + 1,
                                "odd": 4 * n}
    assert set(d["oscillator_generators"]) == {"fermions", "bosons"}
    assert d["central_elements"]["kappa"]["parity"] == 1
    assert d["central_elements"]["K"]["parity"] == 0
    assert d["basis"]["global_order"] == d["basis"]["odd"] + d["basis"]["even"]
    assert set(d["generator_realization"]["realizations"]) == set(d["parity"])
    fresh = build_schema1(n, date=d["metadata"]["generation_date"])
    assert fresh == d, "data file is not reproducible from the generator"


@pytest.mark.parametrize("n", NS)
def test_structure_constants_reproduce_oscillator_brackets(n):
    """Consistency: sum_Z c^Z_{XY} real(Z) == [real(X), real(Y)] exactly, for all pairs."""
    d = load(n)
    alg = OscillatorAlgebra(n)
    R = realizations(n, alg)
    par = d["parity"]
    sc = {}
    for e in d["structure_constants"]:
        assert par[e["Z"]] == (par[e["X"]] + par[e["Y"]]) % 2
        sc.setdefault((e["X"], e["Y"]), []).append((e["Z"], Fraction(e["coeff"])))
    basis = d["basis"]["global_order"]
    for X in basis:
        for Y in basis:
            terms = sc.get((X, Y), [])
            rhs = alg.add(*[R[Z] for Z, _ in terms], coeffs=[c for _, c in terms])
            assert alg.bracket(R[X], R[Y]) == rhs, (X, Y)
