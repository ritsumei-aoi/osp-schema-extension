"""Tests for src/C_evaluate.py (Issue I06)."""
import os
import sys
from fractions import Fraction

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

import C_generators as G  # noqa: E402
import C_evaluate as E  # noqa: E402

NS = [1, 2, 3]


@pytest.mark.parametrize("n", NS)
@pytest.mark.parametrize("profile", E.PROFILES)
def test_files_exist_and_match_schema2(n, profile):
    assert os.path.exists(E.evaluated_path(n, profile))
    assert E.check_against_schema2(n, profile)


@pytest.mark.parametrize("n", NS)
def test_representative_profile(n):
    d = E.load_evaluated(n)
    assert d["profile"] == "all_plus" and d["layer"] == 3
    assert len(d["gb_assignment"]) == 4 * n
    assert all(v == "1" for v in d["gb_assignment"].values())
    assert d["gb_matrix"]["values"] == [["1"] * (2 * n)] * 2


@pytest.mark.parametrize("n", NS)
def test_deformed_constants_zeroth_order_is_schema1(n):
    d = E.load_evaluated(n)
    s1 = G.load_structure(n)
    zero = {(e["X"], e["Y"], e["Z"]): Fraction(e["coeff_0"])
            for e in d["deformed_structure_constants"]["entries"] if e["coeff_0"] != "0"}
    exp = {(e["X"], e["Y"], e["Z"]): Fraction(e["coeff"]) for e in s1["structure_constants"]}
    assert zero == exp
    kap = {(e["X"], e["Y"], e["Z"]): Fraction(e["coeff_kappa"])
           for e in d["deformed_structure_constants"]["entries"] if e["coeff_kappa"] != "0"}
    gam = {(e["X"], e["Y"], e["Z"]): Fraction(e["coeff"]) for e in d["evaluated_gamma"]["entries"]}
    assert kap == gam


@pytest.mark.parametrize("n", NS)
def test_zero_profile_is_undeformed(n):
    d = E.load_evaluated(n, "zero")
    assert d["evaluated_gamma"]["entries"] == []


def test_single_profile_hand_value():
    # gamma(H_2, E_{eps+delta_1}) = -gb_{++} H_2 + gb_{++}/2 K + gb_{+-} E_2del1_p ; single: gb_{++}=1, gb_{+-}=0
    d = E.load_evaluated(1, "single")
    got = {e["Z"]: Fraction(e["coeff"]) for e in d["evaluated_gamma"]["entries"]
           if e["X"] == "H_2" and e["Y"] == "E_eps1_del1_pp"}
    assert got == {"H_2": Fraction(-1), "K": Fraction(1, 2)}
