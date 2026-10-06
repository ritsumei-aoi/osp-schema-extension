"""Tests for Schema 3 (evaluated, I06) and Schema 4 (coboundary, I07)."""

import json
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NS = (1, 2, 3)


def load(n, layer):
    name = {"evaluated": "evaluated", "coboundary": "coboundary"}[layer]
    with open(os.path.join(ROOT, "data", f"C_{n}_{name}.json")) as f:
        return json.load(f)


@pytest.mark.parametrize("n", NS)
def test_evaluated_consistency(n):
    d = load(n, "evaluated")
    for name, ev in d["evaluations"].items():
        assert ev["consistency_with_schema2"] is True, (n, name)


@pytest.mark.parametrize("n", NS)
def test_evaluated_profiles_present(n):
    d = load(n, "evaluated")
    assert "all_plus" in d["evaluations"]
    assert len(d["evaluations"]["all_plus"]["gb_values"]) == 4 * n


@pytest.mark.parametrize("n", NS)
def test_coboundary_present(n):
    d = load(n, "coboundary")
    assert d["layer"] == 4
    assert "delta_f" in d
    assert d["f_map"]["parity"] == "odd"
