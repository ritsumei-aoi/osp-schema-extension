"""I07 tests: Schema 4 coboundary structure."""
import json
import os
import sys
from fractions import Fraction

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from C_coboundary import build_coboundary_json, canonical_f, coboundary, delta_f_pair  # noqa: E402
from C_evaluate import PROFILES, eval_linear_form, profile_values  # noqa: E402
from oscillator import LinPoly  # noqa: E402
from verify_C_structure import BracketTable  # noqa: E402

NS = [1, 2, 3]


@pytest.mark.parametrize("n", NS)
def test_layer4_consistency(n):
    doc, rep = build_coboundary_json(n)
    assert rep["pass"], rep["mismatches"][:3]
    c = doc["consistency"]
    assert c["f_parity_reversing"] and c["delta_f_parity_rule"] and c["labels_in_layer1_basis"]
    assert c["gamma_plus_delta_f_vanishes"]


def test_canonical_f_n1_hand_values():
    f, consts, _ = canonical_f(1)
    g = lambda z: {k: v.to_json() for k, v in f[z].items()}  # noqa: E731
    assert g("E_eps1_del1_pp") == {"H_2": {"gb_a_1_p_b_1_p": "1"}, "E_2del1_p": {"gb_a_1_p_b_1_m": "1"}}
    assert g("H_1") == {"E_eps1_del1_pp": {"gb_a_1_m_b_1_m": "-1"}, "E_eps1_del1_pm": {"gb_a_1_m_b_1_p": "1"},
                        "E_eps1_del1_mp": {"gb_a_1_p_b_1_m": "1"}, "E_eps1_del1_mm": {"gb_a_1_p_b_1_p": "-1"}}
    assert "H_2" not in f and "E_2del1_p" not in f and "E_2del1_m" not in f
    assert consts["E_eps1_del1_pp"].to_json() == {"gb_a_1_p_b_1_p": "-1/2"}


def test_delta_of_zero_is_zero_and_delta_is_linear():
    bt = BracketTable.load(1)
    assert coboundary(bt, {}) == {}
    f, _, _ = canonical_f(1)
    f2 = {z: {k: v * 3 for k, v in vec.items()} for z, vec in f.items()}
    d1, d2 = coboundary(bt, f), coboundary(bt, f2)
    assert set(d1) == set(d2)
    for key in d1:
        assert {k: v * 3 for k, v in d1[key].items()} == d2[key]


def test_delta_f_formula_single_term():
    """Elementary map f(E_eps1_del1_pp) = H_2 only; check (delta f)(H_2, E_eps1_del1_pp) by hand.
    (delta f)(X,Y) = (-1)^{p(X)}[X,f(Y)} - (-1)^{(p(X)+1)p(Y)}[Y,f(X)} - f([X,Y})
    X=H_2 (even), Y=E_pp (odd): [H_2,H_2]=0, f(H_2)=0, [H_2,E_pp] = -E_pp -> f(...) = -H_2 ; result = +H_2."""
    bt = BracketTable.load(1)
    f = {"E_eps1_del1_pp": {"H_2": LinPoly(1)}}
    assert delta_f_pair(bt, f, "H_2", "E_eps1_del1_pp") == {"H_2": LinPoly(1)}


@pytest.mark.parametrize("n", NS)
def test_profile_files_are_substitutions_of_symbolic_file(n):
    sym = json.load(open(os.path.join(ROOT, "data", f"C_{n}_coboundary.json")))
    for prof in PROFILES:
        num = json.load(open(os.path.join(ROOT, "data", f"C_{n}_coboundary_{prof}.json")))
        values = profile_values(n, prof)
        assert num["gb_profile"]["name"] == prof
        expect = {(e["X"], e["Y"], e["Z"]): eval_linear_form(e["coeff"], values) for e in sym["delta_f"]}
        expect = {k: v for k, v in expect.items() if v != 0}
        got = {(e["X"], e["Y"], e["Z"]): Fraction(e["coeff"]) for e in num["delta_f"]}
        assert got == expect


@pytest.mark.parametrize("n", NS)
def test_symbolic_file_matches_generator(n):
    on_disk = json.load(open(os.path.join(ROOT, "data", f"C_{n}_coboundary.json")))
    fresh = json.loads(json.dumps(build_coboundary_json(n)[0]))
    on_disk["metadata"].pop("generation_date")
    fresh["metadata"].pop("generation_date")
    assert on_disk == fresh
