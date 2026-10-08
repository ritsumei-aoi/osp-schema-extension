"""Issue I06: Schema 3 (evaluated structure) tests."""
import json
import os
from fractions import Fraction

import pytest

import C_evaluate as CE
import C_gamma as CG
import C_generators as G
import verify_C_structure as V
from oscillator_algebra import OscillatorAlgebra, gb_labels

NS = [1, 2, 3]


def load(n, name=CE.REPRESENTATIVE):
    p = CE.evaluated_path(n, name)
    assert os.path.exists(p), "run python src/C_evaluate.py"
    return json.load(open(p))


@pytest.mark.parametrize("n", NS)
def test_files_exist_for_all_profiles(n):
    for name in CE.PROFILES:
        d = load(n, name)
        assert d["schema_layer"] == 3 and d["gb_assignment"]["profile"] == name
        assert set(d["gb_assignment"]["values"]) == set(gb_labels(n))


@pytest.mark.parametrize("n", NS)
@pytest.mark.parametrize("name", CE.PROFILES)
def test_consistency_with_schema2(n, name):
    """Re-evaluating the Schema 2 linear forms at the stored gb values reproduces gamma_evaluated."""
    d = load(n, name)
    gb = {l: Fraction(v) for l, v in d["gb_assignment"]["values"].items()}
    s2 = CG.load_schema2(n)
    expected = []
    for e in s2["inhomogeneous_deformation"]["gamma"]:
        c = CG.evaluate_linear_form(e["linear_form"], gb)
        if c != 0:
            expected.append({"X": e["X"], "Y": e["Y"], "Z": e["Z"], "coeff": str(c)})
    assert d["evaluated_structure"]["gamma_evaluated"] == expected


@pytest.mark.parametrize("n", NS)
@pytest.mark.parametrize("name", CE.PROFILES)
def test_deformed_table_splits_into_schema1_and_gamma(n, name):
    d = load(n, name)
    s1 = json.load(open(G.structure_path(n)))
    k0 = [{"X": e["X"], "Y": e["Y"], "Z": e["Z"], "coeff": e["coeff"]}
          for e in d["evaluated_structure"]["deformed_structure_constants"] if e["kappa_power"] == 0]
    k1 = [{"X": e["X"], "Y": e["Y"], "Z": e["Z"], "coeff": e["coeff"]}
          for e in d["evaluated_structure"]["deformed_structure_constants"] if e["kappa_power"] == 1]
    ref0 = [{"X": e["X"], "Y": e["Y"], "Z": e["Z"], "coeff": e["coeff"]} for e in s1["structure_constants"]]
    assert sorted(map(str, k0)) == sorted(map(str, ref0))
    assert sorted(map(str, k1)) == sorted(map(str, d["evaluated_structure"]["gamma_evaluated"]))


@pytest.mark.parametrize("n", NS)
@pytest.mark.parametrize("name", CE.PROFILES)
def test_super_jacobi_of_extended_algebra(n, name):
    d = load(n, name)
    assert d["verification"]["pass"]
    gb = {l: Fraction(v) for l, v in d["gb_assignment"]["values"].items()}
    basis, parity, table = CG.extended_algebra(n, gb)
    res = V.verify(basis, parity, table)
    assert res["pass"]
    assert res["jacobi_triples_checked"] == d["verification"]["jacobi_triples_checked"]


@pytest.mark.parametrize("n", [1, 2])
def test_evaluated_brackets_agree_with_direct_oscillator_computation(n):
    """Independent check: evaluate the deformed brackets directly with numeric gb in the engine."""
    d = load(n, "checkerboard")
    gb = {l: Fraction(v) for l, v in d["gb_assignment"]["values"].items()}
    alg = OscillatorAlgebra(n, deformed=True, gb={l: int(v) for l, v in gb.items()})
    dec = G.Decomposer(n)
    stored = {}
    for e in d["evaluated_structure"]["deformed_structure_constants"]:
        stored.setdefault((e["X"], e["Y"]), {})[(e["kappa_power"], e["Z"])] = Fraction(e["coeff"])
    for X in dec.basis:
        for Y in dec.basis:
            br = alg.bracket(dec.elems[X], dec.elems[Y])
            p0, p1 = alg.split_kappa(br)
            direct = {(0, Z): Fraction(str(c)) for Z, c in dec.decompose(p0).items()}
            direct.update({(1, Z): Fraction(str(c)) for Z, c in dec.decompose(p1).items()})
            assert direct == stored.get((X, Y), {}), (X, Y)


def test_zero_profile_is_undeformed():
    d = load(1, "zero")
    assert d["evaluated_structure"]["gamma_evaluated"] == []
