"""Tests for Schema 3 (evaluated deformation) of C(n+1) (Issue I06)."""
import json
import os
import sys
from fractions import Fraction

import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))

from C_evaluate import PROFILES, direct_gamma, evaluate_gamma, profile_values  # noqa: E402
from C_gamma import gb_labels  # noqa: E402


def load(name):
    with open(os.path.join(ROOT, "data", name)) as fh:
        return json.load(fh)


def fname(n, prof):
    return f"C_{n}_evaluated.json" if prof == "ones" else f"C_{n}_evaluated_{prof}.json"


@pytest.mark.parametrize("n", [1, 2, 3])
@pytest.mark.parametrize("prof", PROFILES)
def test_schema3_consistent_with_schema2(n, prof):
    s1, s2, s3 = load(f"C_{n}_structure.json"), load(f"C_{n}_gamma.json"), load(fname(n, prof))
    assert s3["schema_layer"] == 3 and s3["profile"] == prof
    assert s3["source_gamma"] == f"C_{n}_gamma.json"
    values = {l: Fraction(v) for l, v in s3["gb_assignment"].items()}
    assert list(values) == [l for l, _ in gb_labels(n)]
    assert values == profile_values(prof, n)
    assert s3["evaluated_gamma"] == evaluate_gamma(s2, values)
    k0 = [e for e in s3["deformed_structure_constants"] if e["kappa_order"] == 0]
    k1 = [e for e in s3["deformed_structure_constants"] if e["kappa_order"] == 1]
    assert [{k: e[k] for k in ("X", "Y", "Z", "coeff")} for e in k0] == \
        [{k: e[k] for k in ("X", "Y", "Z", "coeff")} for e in s1["structure_constants"]]
    assert [{k: e[k] for k in ("X", "Y", "Z", "coeff")} for e in k1] == s3["evaluated_gamma"]
    for e in s3["evaluated_gamma"]:
        assert Fraction(e["coeff"]) != 0


@pytest.mark.parametrize("prof", ["ones", "alternating", "single"])
def test_direct_recomputation_n1_n2(prof):
    for n in (1, 2):
        s3 = load(fname(n, prof))
        values = {l: Fraction(v) for l, v in s3["gb_assignment"].items()}
        assert direct_gamma(n, values) == s3["evaluated_gamma"]


def test_single_profile_is_one_column_of_gamma():
    s2, s3 = load("C_1_gamma.json"), load("C_1_evaluated_single.json")
    expected = [{"X": e["X"], "Y": e["Y"], "Z": e["Z"], "coeff": e["coeff"]["gb_a1p_b1p"]}
                for e in s2["inhomogeneous_deformation"]["gamma"] if "gb_a1p_b1p" in e["coeff"]]
    assert s3["evaluated_gamma"] == expected
