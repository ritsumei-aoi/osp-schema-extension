"""Tests for Schema 2 (gamma structure) of C(n+1) (Issue I05)."""
import json
import os
import sys
from fractions import Fraction

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from C_gamma import build_schema2, check_schema2, compute_gamma, gamma_table_from_records  # noqa: E402
from osc_algebra import Poly  # noqa: E402

NS = [1, 2, 3]


def load(name):
    with open(os.path.join(ROOT, "data", name), encoding="utf-8") as fh:
        return json.load(fh)


def g(label, c=1):
    return Poly.symbol(label, Fraction(c))


@pytest.mark.parametrize("n", NS)
def test_schema2_header(n):
    doc = load(f"C_{n}_gamma.json")
    assert doc["schema_version"] == "5.0" and doc["schema_layer"] == 2
    gbm = doc["inhomogeneous_deformation"]["gb_matrix"]
    assert gbm["shape"] == [2, 2 * n] and gbm["count"] == 4 * n
    assert gbm["rows"] == ["a_1_p", "a_1_m"]
    assert gbm["labels"][0][0] == "gb_a1p_b1p" and gbm["labels"][1][-1] == f"gb_a1m_b{n}m"
    assert doc["central_elements"]["kappa"]["parity"] == 1


@pytest.mark.parametrize("n", NS)
def test_schema2_consistency_with_schema1(n):
    doc2, doc1 = load(f"C_{n}_gamma.json"), load(f"C_{n}_structure.json")
    _, br0, _ = compute_gamma(n)
    rep = check_schema2(doc2, doc1, br0)
    assert rep["passed"], rep["failures"]


@pytest.mark.parametrize("n", NS)
def test_schema2_files_are_current(n):
    doc = load(f"C_{n}_gamma.json")
    assert build_schema2(n, today=doc["metadata"]["generation_date"]) == doc


def test_hand_computed_gamma_n1():
    gam = gamma_table_from_records(load("C_1_gamma.json")["gamma"])
    # {a^+ b^-, a^- b^+} = H_1 + kappa (gb_{a^-b^-} a^+b^+ + gb_{a^+b^+} a^-b^-)
    assert gam[("E_eps1_del1_pm", "E_eps1_del1_mp")] == {"E_eps1_del1_pp": g("gb_a1m_b1m"),
                                                         "E_eps1_del1_mm": g("gb_a1p_b1p")}
    # [H_1, a^+ b^+] = 2 a^+b^+ + kappa( -gb_{++} (H_1 + K) - gb_{+-} E_{2δ} )
    assert gam[("H_1", "E_eps1_del1_pp")] == {"H_1": g("gb_a1p_b1p", -1), "E_2del1_p": g("gb_a1p_b1m", -1),
                                              "K": g("gb_a1p_b1p", -1)}
    # {a^+b^+, a^+b^+} = 2 gb_{++} kappa a^+ b^+
    assert gam[("E_eps1_del1_pp", "E_eps1_del1_pp")] == {"E_eps1_del1_pp": g("gb_a1p_b1p", 2)}
    # even-even brackets without fermions are undeformed
    assert ("E_2del1_p", "E_2del1_m") not in gam
    # [H_1, H_2] acquires an odd kappa-term (so(2) generator a^+a^- sees the deformation)
    assert gam[("H_1", "H_2")] == {"E_eps1_del1_pp": g("gb_a1m_b1m"), "E_eps1_del1_pm": g("gb_a1m_b1p"),
                                   "E_eps1_del1_mp": g("gb_a1p_b1m", -1), "E_eps1_del1_mm": g("gb_a1p_b1p", -1)}


def test_gamma_vanishes_when_gb_zero():
    _, _, gam = compute_gamma(2, deformation={})
    assert gam == {}


def test_gamma_only_involves_fermionic_pairs():
    """gamma(X,Y) = 0 whenever neither X nor Y contains a fermion (pure sp(2n) part)."""
    gam = gamma_table_from_records(load("C_2_gamma.json")["gamma"])
    pure_sp = [l for l in load("C_2_structure.json")["basis"]["even"] if l != "H_1" and not l.startswith("H_")]
    pure_sp += ["H_2", "H_3"]          # H_2, H_3 contain no a_1 ; only H_1 does
    for x in pure_sp:
        for y in pure_sp:
            assert (x, y) not in gam, (x, y)
