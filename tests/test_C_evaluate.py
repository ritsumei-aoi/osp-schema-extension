"""Tests for src/C_evaluate.py (I06)."""

import json
import sys
from pathlib import Path

import pytest
import sympy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import C_evaluate as E  # noqa: E402


@pytest.mark.parametrize("n", [1, 2, 3])
def test_consistent_with_schema2(n):
    ok, count = E.check_consistency(n)
    assert ok
    assert count > 0


@pytest.mark.parametrize("n", [1, 2, 3])
def test_file_matches_fresh_evaluation(n):
    data = json.loads((ROOT / "data" / f"C_{n}_evaluated.json").read_text())
    assert data == E.evaluate(n)


def test_zero_profile_gives_empty_evaluation(monkeypatch):
    # Sensitivity: with all gb = 0 every evaluated coefficient vanishes.
    monkeypatch.setitem(E.PROFILES, "zero", lambda n: E.gb_all(n, 0))
    doc = E.evaluate(1, "zero")
    assert doc["evaluated_structure_constants"] == []


def test_all_plus_one_is_unit_substitution():
    doc = E.evaluate(1)
    for e in doc["evaluated_structure_constants"]:
        assert sympy.Rational(e["coeff"]) != 0
    assert all(v == "1" for v in doc["gb_assignment"].values())
