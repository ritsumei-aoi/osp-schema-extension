"""Unit tests for src/C_generators.py (Issue I03) and the oscillator engine."""
import os
import sys
from fractions import Fraction

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

import C_generators as G  # noqa: E402
from osc_algebra import OscAlgebra, ONE  # noqa: E402

NS = [1, 2, 3]

# Ground-truth lists copied verbatim from handover/notation.md §4
NOTATION_EVEN = {
    1: ["H_1", "H_2", "E_2del1_p", "E_2del1_m"],
    2: ["H_1", "H_2", "H_3", "E_2del1_p", "E_2del2_p", "E_del1_del2_pp",
        "E_2del1_m", "E_2del2_m", "E_del1_del2_mm", "E_del1_del2_pm", "E_del1_del2_mp"],
    3: ["H_1", "H_2", "H_3", "H_4",
        "E_2del1_p", "E_2del2_p", "E_2del3_p",
        "E_del1_del2_pp", "E_del1_del3_pp", "E_del2_del3_pp",
        "E_2del1_m", "E_2del2_m", "E_2del3_m",
        "E_del1_del2_mm", "E_del1_del3_mm", "E_del2_del3_mm",
        "E_del1_del2_pm", "E_del1_del3_pm", "E_del2_del3_pm",
        "E_del1_del2_mp", "E_del1_del3_mp", "E_del2_del3_mp"],
}
NOTATION_ODD = {
    1: ["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm"],
    2: ["E_eps1_del1_pp", "E_eps1_del2_pp", "E_eps1_del1_pm", "E_eps1_del2_pm",
        "E_eps1_del1_mp", "E_eps1_del2_mp", "E_eps1_del1_mm", "E_eps1_del2_mm"],
    3: ["E_eps1_del1_pp", "E_eps1_del2_pp", "E_eps1_del3_pp",
        "E_eps1_del1_pm", "E_eps1_del2_pm", "E_eps1_del3_pm",
        "E_eps1_del1_mp", "E_eps1_del2_mp", "E_eps1_del3_mp",
        "E_eps1_del1_mm", "E_eps1_del2_mm", "E_eps1_del3_mm"],
}


@pytest.fixture(scope="module", params=NS)
def schema(request):
    return request.param, G.build_schema1(request.param, date="2026-10-09")


# ----------------------------------------------------------------- basis
@pytest.mark.parametrize("n", NS)
def test_basis_matches_notation(n):
    assert G.even_basis(n) == NOTATION_EVEN[n]
    assert G.odd_basis(n) == NOTATION_ODD[n]


@pytest.mark.parametrize("n", NS)
def test_generator_counts(n):
    assert len(G.even_basis(n)) == 2 * n * n + n + 1
    assert len(G.odd_basis(n)) == 4 * n
    assert len(G.basis(n)) == 2 * n * n + 5 * n + 1
    assert len(set(G.basis(n))) == len(G.basis(n))


@pytest.mark.parametrize("n", NS)
def test_parity(n):
    par = G.parity_map(n)
    alg = OscAlgebra(n)
    R = G.realizations(n)
    for lab in G.basis(n):
        assert par[lab] == alg.element_parity(R[lab])
        assert par[lab] == (1 if lab.startswith("E_eps1") else 0)
    assert sum(par.values()) == 4 * n


# ------------------------------------------------------- oscillator engine
def test_engine_relations():
    alg = OscAlgebra(1)
    a_p, a_m, b_p, b_m = "a_1_p", "a_1_m", "b_1_p", "b_1_m"
    assert alg.normal_form((a_m, a_p)) == {(a_p, a_m): -1, (): 1}
    assert alg.normal_form((b_m, b_p)) == {(b_p, b_m): 1, (): 1}
    assert alg.normal_form((a_p, a_p)) == {}
    assert alg.normal_form(("kappa", "kappa")) == {}
    assert alg.normal_form((b_p, a_p)) == {(a_p, b_p): 1}
    assert alg.normal_form((a_p, "kappa")) == {("kappa", a_p): -1}
    assert alg.normal_form((b_p, "kappa")) == {("kappa", b_p): 1}


# ----------------------------------------------------------- consistency
def test_schema_fields(schema):
    n, d = schema
    for key in ["schema_version", "algebra", "oscillator_generators", "oscillator_relations",
                "central_elements", "basis", "parity", "generator_realization",
                "structure_constants", "metadata"]:
        assert key in d
    assert d["algebra"]["family"] == "C" and d["algebra"]["m"] == 1 and d["algebra"]["n"] == n
    assert d["algebra"]["dimension_formulas"]["even"] == "2n^2 + n + 1"
    assert d["algebra"]["dimension_formulas"]["odd"] == "4n"
    assert d["algebra"]["dimension"] == G.dimensions(n)
    assert d["algebra"]["cartan_type"] == f"C({n+1})"
    assert "supplementary_fermion" not in d["oscillator_generators"]
    assert d["oscillator_generators"]["fermions"]["labels"] == ["a_1_p", "a_1_m"]
    assert d["oscillator_generators"]["fermions"]["m"] == 1
    assert d["oscillator_generators"]["bosons"]["n"] == n
    assert d["central_elements"]["kappa"]["parity"] == 1
    assert d["central_elements"]["K"]["parity"] == 0
    assert d["basis"]["even"] == NOTATION_EVEN[n]
    assert d["basis"]["odd"] == NOTATION_ODD[n]
    assert set(d["parity"]) == set(G.basis(n))
    assert set(d["generator_realization"]["realizations"]) == set(G.basis(n))


def test_structure_constants_well_formed(schema):
    n, d = schema
    B = set(G.basis(n))
    par = d["parity"]
    for e in d["structure_constants"]:
        assert e["X"] in B and e["Y"] in B and e["Z"] in B  # never K
        assert e["sign_rule"] == "graded"
        Fraction(e["coeff"])  # exact rational
        # parity of the bracket matches parity of Z
        assert (par[e["X"]] + par[e["Y"]]) % 2 == par[e["Z"]]


def test_structure_constants_closed_and_graded_antisymmetric(schema):
    n, d = schema
    par = d["parity"]
    table = {}
    for e in d["structure_constants"]:
        table.setdefault((e["X"], e["Y"]), {})[e["Z"]] = Fraction(e["coeff"])
    for (X, Y), v in table.items():
        sign = -1 if (par[X] and par[Y]) else 1
        w = table.get((Y, X), {})
        assert {Z: -sign * c for Z, c in v.items()} == w, (X, Y)


@pytest.mark.parametrize("n", NS)
def test_known_brackets(n):
    table = {}
    for e in G.structure_constants(n):
        table.setdefault((e["X"], e["Y"]), {})[e["Z"]] = Fraction(e["coeff"])
    # Frappat: [E_{alpha_k}, E_{-alpha_k}} = H_k for the odd and bosonic simple roots
    assert table[("E_eps1_del1_pm", "E_eps1_del1_mp")] == {"H_1": 1}
    for k in range(2, n + 1):
        assert table[(f"E_del{k-1}_del{k}_pm", f"E_del{k-1}_del{k}_mp")] == {f"H_{k}": 1}
    # normalization without 1/2: [E_{2delta_n}, E_{-2delta_n}] = 4 H_{n+1}
    assert table[(f"E_2del{n}_p", f"E_2del{n}_m")] == {f"H_{n+1}": 4}
    # Cartan is abelian
    for i in range(1, n + 2):
        for j in range(1, n + 2):
            assert (f"H_{i}", f"H_{j}") not in table
    # [H_1, E_{eps+delta_1}] = 2 E_{eps+delta_1}
    assert table[("H_1", "E_eps1_del1_pp")] == {"E_eps1_del1_pp": 2}


def test_written_files_match_rebuild():
    for n in NS:
        path = G.structure_path(n)
        assert os.path.exists(path), "run python3 src/C_generators.py"
        d = G.load_structure(n)
        assert d["structure_constants"] == G.build_schema1(n)["structure_constants"]
