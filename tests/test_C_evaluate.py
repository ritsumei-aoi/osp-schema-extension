"""Tests for I06: evaluated structure (Schema 3)."""
import json
import os
from fractions import Fraction

import pytest

from C_evaluate import profiles, evaluate_gamma, recompute_gamma, build_schema3, check_profile, DATA_DIR
from C_gamma import load_json

NS = [1, 2, 3]


@pytest.mark.parametrize("n", NS)
def test_profiles_shape(n):
    P = profiles(n)
    assert {"all_plus", "all_minus", "row_sign", "column_sign", "single_a1p_b1p", "generic", "zero"} <= set(P)
    for prof in P.values():
        assert len(prof["values"]) == 4 * n
        for v in prof["values"].values():
            Fraction(v)
    assert set(profiles(n)["all_plus"]["values"].values()) == {"1"}


@pytest.mark.parametrize("n", NS)
@pytest.mark.parametrize("profile", ["all_plus", "single_a1p_b1p", "generic", "zero"])
def test_substitution_equals_recomputation(n, profile):
    assert check_profile(n, profile)


def test_zero_profile_is_undeformed():
    s2 = load_json("C_1_gamma.json")
    assert evaluate_gamma(s2, profiles(1)["zero"]["values"]) == {}


def test_evaluated_values_n1_all_plus():
    s2 = load_json("C_1_gamma.json")
    g = evaluate_gamma(s2, profiles(1)["all_plus"]["values"])
    assert g[("E_eps1_del1_pp", "E_eps1_del1_pp")] == {"E_eps1_del1_pp": Fraction(2)}
    assert g[("H_2", "E_eps1_del1_pp")] == {"H_2": Fraction(-1), "K": Fraction(1, 2), "E_2del1_p": Fraction(1)}


@pytest.mark.parametrize("n", NS)
def test_schema3_files(n):
    rep = load_json(f"C_{n}_evaluated.json")
    assert rep["gb_profile"]["name"] == "all_plus"
    assert rep == load_json(f"C_{n}_evaluated_all_plus.json")
    for prof in profiles(n):
        d = load_json(f"C_{n}_evaluated_{prof}.json")
        assert d == build_schema3(n, prof, date=d["metadata"]["generation_date"])
        assert d["gb_profile"]["matrix"] and len(d["gb_profile"]["matrix"]) == 2
        es = d["evaluated_structure"]
        for e in es["gamma_evaluated"]:
            assert set(e) == {"X", "Y", "Z", "coeff"} and Fraction(e["coeff"]) != 0
        for e in es["deformed_structure_constants"]:
            assert set(e) == {"X", "Y", "Z", "coeff_0", "coeff_kappa"}
