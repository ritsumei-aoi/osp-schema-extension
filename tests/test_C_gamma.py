import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from C_gamma import consistency_report, gb_symbol, normal_order_kappa  # noqa: E402


def test_boson_fermion_contraction_is_minus_gb_kappa():
    # b_1_p a_1_m = a_1_m b_1_p + [b, a] = a_1_m b_1_p - gb_m_1_p * kappa
    out = normal_order_kappa(("b_1_p", "a_1_m"))
    assert out[(0, ("a_1_m", "b_1_p"))] == 1
    assert out[(1, ())] == -gb_symbol("m", 1, "p")


def test_kappa_moves_past_fermion_with_sign():
    # a_1_p b_1_p a_1_m = a_1_p (a_1_m b_1_p - gb_m_1_p kappa)
    #                   = ... + gb_m_1_p * kappa * a_1_p   (kappa a_1_p = -a_1_p kappa)
    out = normal_order_kappa(("a_1_p", "b_1_p", "a_1_m"))
    kappa_terms = {m: c for (k, m), c in out.items() if k == 1}
    assert kappa_terms == {("a_1_p",): gb_symbol("m", 1, "p")}


@pytest.mark.parametrize("n", [1, 2])
def test_consistency_with_schema1(n):
    report = consistency_report(n)
    assert report["entries"] > 0
    assert report["parity_violations"] == 0
    assert report["nonlinear_in_gb"] == 0
    assert report["symmetry_violations"] == 0
    assert report["kappa_free_mismatches"] == 0
