import json
import os
import sys
from fractions import Fraction

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import C_generators as CG  # noqa: E402

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
NS = [1, 2, 3]


@pytest.fixture(scope="module", params=NS)
def schema(request):
    n = request.param
    return n, CG.build_schema1(n, date="2026-01-01")


def test_generator_counts(schema):
    n, d = schema
    assert len(d["basis"]["even"]) == 2 * n * n + n + 1
    assert len(d["basis"]["odd"]) == 4 * n
    assert d["algebra"]["dimension"]["total"] == 2 * n * n + 5 * n + 1
    assert len(d["parity"]) == d["algebra"]["dimension"]["total"]
    assert len(set(d["parity"])) == len(d["parity"])


def test_parity_consistency(schema):
    n, d = schema
    par = d["parity"]
    for x in d["basis"]["even"]:
        assert par[x] == 0
    for x in d["basis"]["odd"]:
        assert par[x] == 1
    for e in d["structure_constants"]:
        assert par[e["Z"]] == (par[e["X"]] + par[e["Y"]]) % 2


def test_antisymmetry(schema):
    n, d = schema
    par = d["parity"]
    sc = {(e["X"], e["Y"], e["Z"]): Fraction(e["coeff"]) for e in d["structure_constants"]}
    for (X, Y, Z), c in sc.items():
        s = -1 if par[X] * par[Y] % 2 == 0 else 1
        assert sc.get((Y, X, Z), 0) == s * c


def test_known_brackets(schema):
    n, d = schema
    sc = {(e["X"], e["Y"], e["Z"]): Fraction(e["coeff"]) for e in d["structure_constants"]}
    assert sc[(f"E_2del{n}_p", f"E_2del{n}_m", f"H_{n+1}")] == 1
    assert sc[("H_1", "E_eps1_del1_pp", "E_eps1_del1_pp")] == 2
    if n == 1:
        # {a+b+, a-b-} = b+b- - a+a- + 1 = -H_1 - 2 H_2
        assert sc[("E_eps1_del1_pp", "E_eps1_del1_mm", "H_1")] == -1
        assert sc[("E_eps1_del1_pp", "E_eps1_del1_mm", "H_2")] == -2


def test_realization_uses_standard_fermion_pair(schema):
    n, d = schema
    assert "supplementary_fermion" not in d["oscillator_generators"]
    assert d["oscillator_generators"]["fermions"]["labels"] == ["a_1_p", "a_1_m"]
    assert len(d["oscillator_generators"]["bosons"]["labels"]) == 2 * n
    assert set(d["central_elements"]) == {"kappa", "K"}
    assert d["central_elements"]["kappa"]["parity"] == 1 and d["central_elements"]["K"]["parity"] == 0
    assert d["algebra"]["m"] == 1 and d["algebra"]["family"] == "C"


def test_top_level_keys(schema):
    n, d = schema
    assert list(d) == ["schema_version", "algebra", "oscillator_generators", "oscillator_relations",
                       "central_elements", "basis", "parity", "generator_realization",
                       "structure_constants", "metadata"]


@pytest.mark.parametrize("n", NS)
def test_data_files_match_generator(n):
    on_disk = json.load(open(os.path.join(DATA, f"C_{n}_structure.json")))
    fresh = CG.build_schema1(n, date=on_disk["metadata"]["generation_date"])
    assert on_disk == json.loads(json.dumps(fresh, ensure_ascii=False))


def test_closure_no_residual():
    # structure_constants raises if any bracket leaves the span of the basis
    for n in NS:
        CG.structure_constants(n)
