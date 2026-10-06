import json
import os
from fractions import Fraction

import pytest

from conftest import DATA
from C_evaluate import build_schema3, gb_profiles


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema3_file(n):
    with open(os.path.join(DATA, f"C_{n}_evaluated.json")) as fh:
        d = json.load(fh)
    fresh = build_schema3(n, direct_check=(n < 3))
    d["metadata"].pop("generation_date")
    fresh["metadata"].pop("generation_date")
    for p, q in zip(d["profiles"], fresh["profiles"]):
        assert p["check_direct_oscillator_substitution"] is True
        for key in ("name", "gb_values", "gamma_evaluated", "gamma_central_evaluated"):
            assert p[key] == q[key]
    assert d["primary_profile"] == "all_plus"
    assert [p["name"] for p in d["profiles"]] == [p[0] for p in gb_profiles(n)]
    assert all(len(p["gb_values"]) == 4 * n for p in d["profiles"])


@pytest.mark.parametrize("n", [1, 2, 3])
def test_linearity_against_schema2(n):
    """gamma(all_minus) = -gamma(all_plus); zero profile has no deformation."""
    with open(os.path.join(DATA, f"C_{n}_evaluated.json")) as fh:
        d = json.load(fh)
    prof = {p["name"]: p for p in d["profiles"]}
    plus = {(e["X"], e["Y"], e["Z"]): Fraction(e["coeff"]) for e in prof["all_plus"]["gamma_evaluated"]}
    minus = {(e["X"], e["Y"], e["Z"]): Fraction(e["coeff"]) for e in prof["all_minus"]["gamma_evaluated"]}
    assert minus == {k: -v for k, v in plus.items()}
    assert prof["zero"]["gamma_evaluated"] == [] and prof["zero"]["gamma_central_evaluated"] == []
