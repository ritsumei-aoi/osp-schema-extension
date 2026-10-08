"""Tests for src/C_gamma.py (Issue I05)."""
import os
import sys
from fractions import Fraction

import pytest
import sympy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

import C_generators as G  # noqa: E402
import C_gamma as Gm  # noqa: E402

NS = [1, 2, 3]


@pytest.fixture(scope="module", params=NS)
def gamma_doc(request):
    n = request.param
    return n, Gm.load_gamma(n)


def test_gb_matrix(gamma_doc):
    n, d = gamma_doc
    m = d["gb_matrix"]
    assert m["shape"] == [2, 2 * n] and m["count"] == 4 * n
    assert m["rows"] == ["a_1_p", "a_1_m"]
    assert m["labels"][0][0] == "gb_a1p_b1p" and m["labels"][1][-1] == f"gb_a1m_b{n}m"
    flat = [x for row in m["labels"] for x in row]
    assert len(set(flat)) == 4 * n


def test_entries_well_formed(gamma_doc):
    n, d = gamma_doc
    B = set(G.basis(n)) | {"K"}
    par = G.parity_map(n)
    par["K"] = 0
    labels = {x for row in d["gb_matrix"]["labels"] for x in row}
    for e in d["inhomogeneous_deformation"]["entries"]:
        assert e["X"] in B - {"K"} and e["Y"] in B - {"K"} and e["Z"] in B
        # gamma carries parity |X|+|Y|+1 (kappa is odd)
        assert (par[e["X"]] + par[e["Y"]] + 1) % 2 == par[e["Z"]]
        lf = e["linear_form"]
        assert lf and set(lf) <= labels
        for c in lf.values():
            Fraction(c)
        # coeff string and linear form agree
        expr = sympy.sympify(e["coeff"])
        rebuilt = sum(sympy.Rational(c) * sympy.Symbol(g) for g, c in lf.items())
        assert sympy.expand(expr - rebuilt) == 0


def test_consistency_flags(gamma_doc):
    n, d = gamma_doc
    assert d["consistency"]["zeroth_order_equals_schema1"] is True
    assert d["consistency"]["gamma_graded_antisymmetric"] is True
    assert d["consistency"]["entries_with_Z_K"] > 0  # K components exist (see I05 response)


def test_gamma_hand_values_n1():
    """gamma(H_2, E_{eps+delta_1}) = -gb_{++} H_2 + gb_{++}/2 K + gb_{+-} E_{2delta_1}  (hand computation)."""
    d = Gm.load_gamma(1)
    got = {e["Z"]: e["coeff"] for e in d["inhomogeneous_deformation"]["entries"]
           if e["X"] == "H_2" and e["Y"] == "E_eps1_del1_pp"}
    exp = {"H_2": "-gb_a1p_b1p", "K": "gb_a1p_b1p/2", "E_2del1_p": "gb_a1p_b1m"}
    assert {k: sympy.sympify(v) for k, v in got.items()} == {k: sympy.sympify(v) for k, v in exp.items()}
    # gamma(E_{-2delta_1}, E_{eps+delta_1}) = 2 gb_{+-} H_2 - gb_{+-} K
    got = {e["Z"]: e["coeff"] for e in d["inhomogeneous_deformation"]["entries"]
           if e["X"] == "E_2del1_m" and e["Y"] == "E_eps1_del1_pp"}
    assert {k: sympy.sympify(v) for k, v in got.items()} == {
        "H_2": sympy.sympify("2*gb_a1p_b1m"), "K": sympy.sympify("-gb_a1p_b1m")}


@pytest.mark.parametrize("n", [1, 2])
def test_rebuild_matches_file(n):
    fresh = Gm.build_schema2(n, date="x")["inhomogeneous_deformation"]["entries"]
    stored = Gm.load_gamma(n)["inhomogeneous_deformation"]["entries"]
    assert fresh == stored
