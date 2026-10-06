import json
import os

import pytest

from C_evaluate import build_schema3, check_against_schema2, gb_profiles
from C_generators import DATA_DIR


@pytest.mark.parametrize("n", [1, 2, 3])
def test_profiles_cover_all_parameters(n):
    for vals in gb_profiles(n).values():
        assert len(vals) == 4 * n
        assert set(vals.values()) <= {-1, 0, 1}


@pytest.mark.parametrize("n", [1, 2, 3])
def test_evaluated_json_consistent_with_schema2(n):
    with open(os.path.join(DATA_DIR, f"C_{n}_evaluated.json")) as f:
        d3 = json.load(f)
    assert d3["layer"] == 3
    assert check_against_schema2(n, d3) == 0
    assert d3["profiles"]["zero"]["n_gamma_entries"] == 0
    # gamma is linear in gb: all_minus is exactly -all_plus
    plus = {(e["X"], e["Y"], e["Z"]): e["coeff"] for e in d3["profiles"]["all_plus"]["gamma"]}
    minus = {(e["X"], e["Y"], e["Z"]): e["coeff"] for e in d3["profiles"]["all_minus"]["gamma"]}
    assert plus.keys() == minus.keys()
    assert all(minus[k] == (v[1:] if v.startswith("-") else "-" + v) for k, v in plus.items())


def test_json_matches_generator():
    with open(os.path.join(DATA_DIR, "C_1_evaluated.json")) as f:
        d3 = json.load(f)
    assert d3["profiles"] == build_schema3(1)["profiles"]
