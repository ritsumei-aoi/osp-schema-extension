"""Tests for Schema 4 (coboundary structure) of C(n+1) (Issue I07)."""
import json
import os
import sys
from fractions import Fraction

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from C_coboundary import build_schema4, canonical_f, check_odd_map, check_schema4, delta_f  # noqa: E402
from C_evaluate import gb_profile  # noqa: E402
from C_gamma import bracket_table_from_schema1, gamma_table_from_records, _padd, _pscale  # noqa: E402
from osc_algebra import Poly  # noqa: E402

NS = [1, 2, 3]


def load(name):
    with open(os.path.join(ROOT, "data", name), encoding="utf-8") as fh:
        return json.load(fh)


def g(label, c=1):
    return Poly.symbol(label, Fraction(c))


@pytest.mark.parametrize("n", NS)
@pytest.mark.parametrize("suffix", ["", "_alternating"])
def test_schema4_consistency_and_layer3(n, suffix):
    doc4 = load(f"C_{n}_coboundary{suffix}.json")
    doc1 = load(f"C_{n}_structure.json")
    doc3 = load(f"C_{n}_evaluated{suffix}.json")
    assert doc4["schema_layer"] == 4 and doc4["source_evaluated"] == f"C_{n}_evaluated{suffix}.json"
    assert doc4["odd_map_f"]["phi_count"] == 2 * (2 * n * n + n + 1) * 4 * n
    rep = check_schema4(doc4, doc1, doc3)
    assert rep["passed"], rep["failures"]
    assert rep["counts"]["layer3_mismatching_pairs"] == 0


@pytest.mark.parametrize("n", NS)
def test_schema4_files_are_current(n):
    doc4 = load(f"C_{n}_coboundary.json")
    assert build_schema4(n, "all_plus_one", today=doc4["metadata"]["generation_date"]) == doc4


def test_canonical_f_closed_form_n1():
    f = canonical_f(1, "symbolic")
    # f_can(a^+ b^+) = -c^+ b^+ = -gb_{+-} (b^+)^2 + gb_{++} b^- b^+ ,  b^-b^+ = b^+b^- + 1 = -H_2 + K/2
    assert f["E_eps1_del1_pp"] == {"E_2del1_p": g("gb_a1p_b1m", -1), "H_2": g("gb_a1p_b1p", -1), "K": g("gb_a1p_b1p", "1/2")}
    assert f["H_1"] == {"E_eps1_del1_pp": g("gb_a1m_b1m"), "E_eps1_del1_pm": g("gb_a1m_b1p", -1),
                        "E_eps1_del1_mp": g("gb_a1p_b1m", -1), "E_eps1_del1_mm": g("gb_a1p_b1p")}
    assert "E_2del1_p" not in f and "H_2" not in f


@pytest.mark.parametrize("n", NS)
def test_gamma_equals_delta_f_can_symbolically(n):
    """gamma = delta f_can as an identity in the gb symbols (all gb at once)."""
    doc1, doc2 = load(f"C_{n}_structure.json"), load(f"C_{n}_gamma.json")
    labels, par = doc1["basis"]["pbw_order"], doc1["parity"]
    br = bracket_table_from_schema1(doc1)
    f = canonical_f(n, "symbolic")
    assert not check_odd_map(f, par)
    df = delta_f(f, br, labels, par)
    gam = gamma_table_from_records(doc2["gamma"])
    for key in set(df) | set(gam):
        assert not _padd(df.get(key, {}), _pscale(gam.get(key, {}), -1)), key


def test_delta_of_inner_derivation_is_zero():
    """For odd Z, f = ad_Z (X -> [Z, X]) is an odd 1-cocycle: delta f = 0."""
    doc1 = load("C_2_structure.json")
    labels, par = doc1["basis"]["pbw_order"], doc1["parity"]
    br = bracket_table_from_schema1(doc1)
    Z = "E_eps1_del2_mp"
    f = {x: {w: Poly.const(c) for w, c in br.get((Z, x), {}).items()} for x in labels}
    f = {x: v for x, v in f.items() if v}
    assert delta_f(f, br, labels, par) == {}


def test_delta_f_without_K_has_no_K_component():
    doc1 = load("C_1_structure.json")
    labels, par = doc1["basis"]["pbw_order"], doc1["parity"]
    br = bracket_table_from_schema1(doc1)
    f = canonical_f(1, gb_profile(1, "all_plus_one"))
    f_g = {s: {t: c for t, c in comps.items() if t != "K"} for s, comps in f.items()}
    df = delta_f(f_g, br, labels, par)
    assert all("K" not in comps for comps in df.values())
