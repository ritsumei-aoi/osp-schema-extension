"""Tests for src/C_coboundary.py (Issue I07)."""
import os
import sys
from fractions import Fraction

import pytest
import sympy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

import C_generators as G  # noqa: E402
import C_gamma as Gm  # noqa: E402
import C_evaluate as E  # noqa: E402
import C_coboundary as C  # noqa: E402

NS = [1, 2, 3]


def _sym(entries):
    return {(e["X"], e["Y"], e["Z"]): sympy.sympify(e["coeff"]) for e in entries}


@pytest.mark.parametrize("n", NS)
def test_layer1_consistency(n):
    assert C.check_layer1_consistency(n)
    d = C.load_coboundary(n)
    assert d["summary"]["f_even_to_odd_parity_ok"] is True
    B = set(G.basis(n))
    par = G.parity_map(n)
    for Z, vec in d["f_map"]["entries"].items():
        assert Z in B
        for Zi in vec:
            assert Zi in B and par[Zi] == 1 - par[Z]
    for e in d["coboundary"]["entries"]:
        assert e["Z"] in B
        Fraction(e["coeff"])


@pytest.mark.parametrize("n", NS)
def test_f_is_defined_on_whole_basis(n):
    d = C.load_coboundary(n)
    assert set(d["f_map"]["entries"]) == set(G.basis(n))
    # odd generators have a K component, even ones do not
    lam = d["f_K_component"]["entries"]
    assert set(lam) == set(G.odd_basis(n))


def test_f_hand_values_n1():
    s = C.load_coboundary(1)["symbolic"]
    fm, lam = s["f_map"], s["f_K_component"]
    # f(E_{eps+delta_1}) = gb_{++} (N_a - 1/2) + gb_{++}/2 K ; N_a - 1/2 = H_1 + H_2  (n=1)
    assert {k: sympy.sympify(v) for k, v in fm["E_eps1_del1_pp"].items()} == {
        "H_1": sympy.sympify("gb_a1p_b1p"), "H_2": sympy.sympify("gb_a1p_b1p")}
    assert sympy.sympify(lam["E_eps1_del1_pp"]) == sympy.sympify("gb_a1p_b1p/2")
    # f(E_{-eps-delta_1}) = -gb_{--}(N_a - 1/2) + gb_{--}/2 K
    assert {k: sympy.sympify(v) for k, v in fm["E_eps1_del1_mm"].items()} == {
        "H_1": sympy.sympify("-gb_a1m_b1m"), "H_2": sympy.sympify("-gb_a1m_b1m")}
    assert sympy.sympify(lam["E_eps1_del1_mm"]) == sympy.sympify("gb_a1m_b1m/2")
    # f(E_{2 delta_1}) = -F((b^+)^2) = -2 (gb_{+,1,+} a^- b^+ + gb_{-,1,+} a^+ b^+)
    assert {k: sympy.sympify(v) for k, v in fm["E_2del1_p"].items()} == {
        "E_eps1_del1_mp": sympy.sympify("-2*gb_a1p_b1p"),
        "E_eps1_del1_pp": sympy.sympify("-2*gb_a1m_b1p")}


@pytest.mark.parametrize("n", NS)
def test_symbolic_gamma_equals_delta_f_on_g_and_K(n):
    """The central result used in I08: gamma|_g = delta f (strict), gamma|_K = K-extension."""
    s = C.load_coboundary(n)["symbolic"]
    gam = _sym(Gm.load_gamma(n)["inhomogeneous_deformation"]["entries"])
    cob = _sym(s["coboundary_entries"])
    kext = _sym(s["K_extension_entries"])
    gam_g = {k: v for k, v in gam.items() if k[2] != "K"}
    gam_K = {k: v for k, v in gam.items() if k[2] == "K"}
    assert gam_g == cob
    assert gam_K == kext
    assert len(gam_K) > 0


@pytest.mark.parametrize("n", NS)
@pytest.mark.parametrize("profile", E.PROFILES)
def test_evaluated_files_match_symbolic_substitution(n, profile):
    d = C.load_coboundary(n, profile)
    s = C.load_coboundary(n)["symbolic"]
    subs = {sympy.Symbol(l): sympy.Rational(v) for l, v in d["gb_assignment"].items()}
    exp = {k: sympy.expand(v.subs(subs)) for k, v in _sym(s["coboundary_entries"]).items()}
    exp = {k: v for k, v in exp.items() if v != 0}
    assert _sym(d["coboundary"]["entries"]) == exp
