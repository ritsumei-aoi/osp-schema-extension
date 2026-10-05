"""Tests for C(n+1) structure constant generator."""

import json
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from C_generators import build_basis, get_parity, generate_schema1_json


DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')


@pytest.mark.parametrize("n,expected_even,expected_odd", [
    (1, 4, 4),
    (2, 11, 8),
    (3, 22, 12),
])
def test_basis_counts(n, expected_even, expected_odd):
    even, odd = build_basis(n)
    assert len(even) == expected_even, f"n={n}: even count {len(even)} != {expected_even}"
    assert len(odd) == expected_odd, f"n={n}: odd count {len(odd)} != {expected_odd}"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_parity_consistency(n):
    even, odd = build_basis(n)
    for g in even:
        assert get_parity(g) == 0, f"{g} should have parity 0"
    for g in odd:
        assert get_parity(g) == 1, f"{g} should have parity 1"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_dimension_formulas(n):
    even, odd = build_basis(n)
    expected_even = 2 * n * n + n + 1
    expected_odd = 4 * n
    expected_total = expected_even + expected_odd
    assert len(even) == expected_even
    assert len(odd) == expected_odd
    assert len(even) + len(odd) == expected_total


@pytest.mark.parametrize("n", [1, 2, 3])
def test_no_raw_entries(n):
    filename = os.path.join(DATA_DIR, f"C_{n}_structure.json")
    with open(filename) as f:
        data = json.load(f)
    for sc in data["structure_constants"]:
        assert not sc["Z"].startswith("raw_"), f"Raw entry found: {sc}"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema_structure(n):
    filename = os.path.join(DATA_DIR, f"C_{n}_structure.json")
    with open(filename) as f:
        data = json.load(f)
    assert data["schema_version"] == "5.0"
    assert data["algebra"]["family"] == "C"
    assert data["algebra"]["m"] == 1
    assert data["algebra"]["n"] == n
    assert "fermions" in data["oscillator_generators"]
    assert "bosons" in data["oscillator_generators"]
    assert "central_elements" in data
    assert "kappa" in data["central_elements"]
    assert "K" in data["central_elements"]


@pytest.mark.parametrize("n", [1, 2, 3])
def test_structure_constants_graded_antisymmetry(n):
    filename = os.path.join(DATA_DIR, f"C_{n}_structure.json")
    with open(filename) as f:
        data = json.load(f)
    parity = data["parity"]
    sc_map = {}
    for sc in data["structure_constants"]:
        key = (sc["X"], sc["Y"], sc["Z"])
        sc_map[key] = sc["coeff"]

    for sc in data["structure_constants"]:
        X, Y, Z = sc["X"], sc["Y"], sc["Z"]
        px, py = parity[X], parity[Y]
        expected_sign = (-1) ** (px * py + 1)
        rev_key = (Y, X, Z)
        if rev_key in sc_map:
            from fractions import Fraction
            c1 = Fraction(sc["coeff"])
            c2 = Fraction(sc_map[rev_key])
            assert c1 == expected_sign * c2, f"Antisymmetry failed for [{X},{Y}] -> {Z}"
