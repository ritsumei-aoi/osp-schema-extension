import json
import os
import sys
from fractions import Fraction

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from C_generators import (CAlgebra, build_schema1, dims, even_basis, odd_basis,  # noqa: E402
                          parity_map, pbw_basis)
from oscillator_algebra import OscillatorAlgebra, poly_const  # noqa: E402

NS = [1, 2, 3]
TOP_KEYS = {"schema_version", "algebra", "oscillator_generators", "oscillator_relations",
            "central_elements", "basis", "parity", "generator_realization",
            "structure_constants", "metadata"}


@pytest.fixture(scope="module", params=NS)
def schema(request):
    return build_schema1(request.param, date="test")


@pytest.mark.parametrize("n", NS)
def test_counts(n):
    d = dims(n)
    assert len(even_basis(n)) == d["even"] == 2 * n * n + n + 1
    assert len(odd_basis(n)) == d["odd"] == 4 * n
    assert len(set(pbw_basis(n))) == d["total"] == 2 * n * n + 5 * n + 1
    assert {1: 8, 2: 19, 3: 34}[n] == d["total"]


@pytest.mark.parametrize("n", NS)
def test_parity(n):
    p = parity_map(n)
    assert all(p[x] == 0 for x in even_basis(n))
    assert all(p[x] == 1 for x in odd_basis(n))
    calg = CAlgebra(n)
    for x in calg.basis:  # parity of realization matches label parity
        assert calg.alg.elem_parity(calg.real[x]) == p[x]


def test_basis_lists_match_notation():
    assert even_basis(1) == ["H_1", "H_2", "E_2del1_p", "E_2del1_m"]
    assert odd_basis(2) == ["E_eps1_del1_pp", "E_eps1_del2_pp", "E_eps1_del1_pm",
                            "E_eps1_del2_pm", "E_eps1_del1_mp", "E_eps1_del2_mp",
                            "E_eps1_del1_mm", "E_eps1_del2_mm"]
    assert even_basis(2) == ["H_1", "H_2", "H_3", "E_2del1_p", "E_2del2_p", "E_del1_del2_pp",
                             "E_2del1_m", "E_2del2_m", "E_del1_del2_mm", "E_del1_del2_pm",
                             "E_del1_del2_mp"]


def test_oscillator_relations():
    alg = OscillatorAlgebra(2)
    one = {(): poly_const(1)}
    e = lambda s: {(s,): poly_const(1)}  # noqa: E731
    assert alg.bracket(e("a_1_m"), e("a_1_p")) == one          # {a-, a+} = 1
    assert alg.bracket(e("a_1_p"), e("a_1_p")) == {}           # {a+, a+} = 0
    assert alg.bracket(e("b_1_m"), e("b_1_p")) == one          # [b-, b+] = 1
    assert alg.bracket(e("b_1_m"), e("b_2_p")) == {}
    assert alg.bracket(e("b_1_p"), e("a_1_p")) == {}           # undeformed
    dalg = OscillatorAlgebra(2, deformed=True)
    r = dalg.bracket(e("b_2_m"), e("a_1_p"))
    assert r == {("kappa",): {("gb_a1p_b2m",): Fraction(-1)}}
    assert dalg.mul(e("kappa"), e("kappa")) == {}
    assert dalg.mul(e("a_1_p"), e("kappa")) == {("kappa", "a_1_p"): poly_const(-1)}


def test_top_level_keys(schema):
    assert set(schema) == TOP_KEYS
    a = schema["algebra"]
    assert a["family"] == "C" and a["m"] == 1
    assert set(schema["oscillator_generators"]) == {"fermions", "bosons"}
    assert schema["oscillator_generators"]["fermions"]["labels"] == ["a_1_p", "a_1_m"]
    ce = schema["central_elements"]
    assert ce["kappa"]["parity"] == 1 and ce["K"]["parity"] == 0
    assert set(schema["generator_realization"]["realizations"]) == set(schema["parity"])


def test_structure_constants_conform(schema):
    basis = set(schema["basis"]["ordering"])
    p = schema["parity"]
    for e in schema["structure_constants"]:
        assert set(e) == {"X", "Y", "Z", "coeff", "sign_rule"}
        assert e["X"] in basis and e["Y"] in basis and e["Z"] in basis
        assert Fraction(e["coeff"]) != 0
        assert p[e["Z"]] == (p[e["X"]] + p[e["Y"]]) % 2  # grading


def test_known_brackets():
    s = build_schema1(1, date="test")
    sc = {(e["X"], e["Y"], e["Z"]): Fraction(e["coeff"]) for e in s["structure_constants"]}
    assert sc[("E_eps1_del1_pp", "E_eps1_del1_mm", "H_1")] == -1
    assert sc[("E_eps1_del1_pp", "E_eps1_del1_mm", "H_2")] == -2
    assert sc[("E_2del1_p", "E_2del1_m", "H_2")] == 4
    assert sc[("H_1", "E_2del1_p", "E_2del1_p")] == 2


@pytest.mark.parametrize("n", NS)
def test_data_files_match_generator(n):
    path = os.path.join(ROOT, "data", f"C_{n}_structure.json")
    with open(path) as fh:
        stored = json.load(fh)
    fresh = build_schema1(n, date=stored["metadata"]["generation_date"])
    assert stored == json.loads(json.dumps(fresh))
