"""Tests for Schema 3 (Issue I06)."""
import json
import os

import pytest

from conftest import DATA
from C_evaluate import build_schema3, check_against_engine, sign_profiles


def load(n):
    with open(os.path.join(DATA, f"C_{n}_evaluated.json")) as f:
        return json.load(f)


@pytest.mark.parametrize("n", (1, 2, 3))
def test_evaluated_reproducible_and_consistent(n):
    d = load(n)
    assert d["layer"] == 3 and d["gamma_ref"] == f"C_{n}_gamma.json"
    assert build_schema3(n, date=d["metadata"]["generation_date"]) == d
    assert set(check_against_engine(n, d).values()) == {0}


@pytest.mark.parametrize("n", (1, 2, 3))
def test_profiles_are_sign_assignments(n):
    for name, (_, gb) in sign_profiles(n).items():
        assert len(gb) == 4 * n
        assert set(gb.values()) <= {-1, 0, 1}
        if name in ("all_plus", "all_minus", "row_split", "column_split", "alternating_j",
                    "checkerboard"):
            assert set(gb.values()) <= {-1, 1}


def test_zero_profile_is_undeformed():
    d = load(2)
    zero = next(p for p in d["evaluation"]["profiles"] if p["name"] == "zero")
    assert zero["gamma_evaluated"] == []
