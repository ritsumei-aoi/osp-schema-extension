import json
import os
import sys
from fractions import Fraction

import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))

import C_evaluate as E  # noqa: E402
import C_gamma as CG  # noqa: E402
import C_generators as G  # noqa: E402

NS = [1, 2, 3]


def load(n, suffix=""):
    with open(os.path.join(ROOT, "data", f"C_{n}_evaluated{suffix}.json")) as f:
        return json.load(f)


@pytest.mark.parametrize("n", NS)
def test_canonical_file_is_all_plus(n):
    d = load(n)
    assert d["layer"] == "evaluated"
    assert d["gb_assignment"]["profile"] == "all_plus"
    assert set(d["gb_assignment"]["values"].values()) == {"1"}
    assert len(d["gb_assignment"]["values"]) == 4 * n


@pytest.mark.parametrize("n", NS)
@pytest.mark.parametrize("profile", E.PROFILES)
def test_matches_schema2_and_direct(n, profile):
    gb = E.profile_values(n, profile)
    assert E.evaluate_from_schema2(n, gb) == E.evaluate_direct(n, gb)


@pytest.mark.parametrize("n", NS)
def test_files_match_regeneration(n):
    for profile in E.PROFILES:
        suffix = "" if profile == "all_plus" else f"_{profile}"
        assert E.build_schema3(n, profile)["evaluated_deformation"] == \
            load(n, suffix)["evaluated_deformation"]


@pytest.mark.parametrize("n", NS)
def test_zero_profile_is_empty_and_parity(n):
    assert load(n, "_zero")["evaluated_deformation"]["gamma"] == []
    for e in load(n)["evaluated_deformation"]["gamma"]:
        assert G.parity_of(e["Z"]) == (G.parity_of(e["X"]) + G.parity_of(e["Y"]) + 1) % 2
        assert Fraction(e["coeff"]) != 0
