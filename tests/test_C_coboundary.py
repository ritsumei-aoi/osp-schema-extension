"""Tests for I07: odd linear map f and its coboundary (Schema 4)."""
import json
import os
from fractions import Fraction

import pytest

from oscillator_algebra import Poly
from C_coboundary import canonical_f, coboundary, check_f_odd, build_schema4, DATA_DIR
from C_evaluate import profiles, evaluate_gamma
from C_gamma import load_json

NS = [1, 2, 3]


@pytest.fixture(scope="module")
def canon():
    return {n: canonical_f(n) for n in NS}


@pytest.mark.parametrize("n", NS)
def test_f_is_odd_and_reproduces_gamma(canon, n):
    B, table, gamma, f, sign = canon[n]
    assert sign == -1
    assert check_f_odd(B, f)
    assert coboundary(B.labels, B.parity, table, f) == gamma


def test_f_values_n1(canon):
    B, table, gamma, f, sign = canon[1]
    gpp, gmp = Poly.var("gb_a1p_b1p"), Poly.var("gb_a1m_b1p")
    assert f["E_eps1_del1_pp"] == {"H_1": gpp, "H_2": gpp, "K": gpp * Poly.const("1/2")}
    assert f["E_2del1_p"] == {"E_eps1_del1_pp": -2 * gmp, "E_eps1_del1_mp": -2 * gpp}


def test_coboundary_of_zero_map_is_zero(canon):
    B, table, gamma, f, sign = canon[1]
    assert coboundary(B.labels, B.parity, table, {}) == {}


def test_coboundary_is_linear_in_f(canon):
    B, table, gamma, f, sign = canon[1]
    f2 = {x: {z: 3 * c for z, c in comps.items()} for x, comps in f.items()}
    df2 = coboundary(B.labels, B.parity, table, f2)
    assert df2 == {k: {z: 3 * c for z, c in v.items()} for k, v in gamma.items()}


def test_delta_of_K_valued_map_is_minus_f_of_bracket(canon):
    """For f with values only in K, (delta f)(X,Y) = -f([X,Y]) (central terms drop out)."""
    B, table, gamma, f, sign = canon[1]
    fK = {"E_eps1_del1_pp": {"K": Poly.const(1)}}
    df = coboundary(B.labels, B.parity, table, fK)
    for (x, y), comps in df.items():
        assert set(comps) == {"K"}
        assert comps["K"] == -table[(x, y)]["E_eps1_del1_pp"]


@pytest.mark.parametrize("n", NS)
def test_schema4_files_and_profile_consistency(n):
    d = load_json(f"C_{n}_coboundary.json")
    assert d == build_schema4(n, date=d["metadata"]["generation_date"])
    assert d["odd_linear_map"]["SIGN"] == -1
    assert d["coboundary"]["equals_gamma_symbolically"] is True
    s2 = load_json(f"C_{n}_gamma.json")
    for prof in profiles(n):
        dp = load_json(f"C_{n}_coboundary_{prof}.json")
        assert dp["gb_profile"]["name"] == prof
        got = {}
        for e in dp["coboundary"]["entries"]:
            got.setdefault((e["X"], e["Y"]), {})[e["Z"]] = Fraction(e["coeff"])
        # Layer 4 evaluated at the profile == Layer 3 gamma at the profile
        assert got == evaluate_gamma(s2, profiles(n)[prof]["values"])
        # and == the Layer 3 file on disk
        s3 = load_json(f"C_{n}_evaluated_{prof}.json")
        disk = {}
        for e in s3["evaluated_structure"]["gamma_evaluated"]:
            disk.setdefault((e["X"], e["Y"]), {})[e["Z"]] = Fraction(e["coeff"])
        assert got == disk
