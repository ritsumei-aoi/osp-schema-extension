"""Tests for C(n+1) structure constant generator."""

import json
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from C_generators import build_basis, get_parity, build_schema1_json, get_realization
from fractions import Fraction


@pytest.mark.parametrize("n,expected_even,expected_odd", [
    (1, 4, 4),
    (2, 11, 8),
    (3, 22, 12),
])
def test_basis_counts(n, expected_even, expected_odd):
    even, odd = build_basis(n)
    assert len(even) == expected_even, f"n={n}: even count {len(even)} != {expected_even}"
    assert len(odd) == expected_odd, f"n={n}: odd count {len(odd)} != {expected_odd}"


@pytest.mark.parametrize("n,expected_total", [
    (1, 8),
    (2, 19),
    (3, 34),
])
def test_total_dimension(n, expected_total):
    even, odd = build_basis(n)
    assert len(even) + len(odd) == expected_total


@pytest.mark.parametrize("n", [1, 2, 3])
def test_dimension_formula(n):
    even, odd = build_basis(n)
    assert len(even) == 2 * n * n + n + 1
    assert len(odd) == 4 * n


@pytest.mark.parametrize("n", [1, 2, 3])
def test_parity_assignment(n):
    even, odd = build_basis(n)
    for g in even:
        assert get_parity(g) == 0, f"{g} should be even"
    for g in odd:
        assert get_parity(g) == 1, f"{g} should be odd"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_no_duplicate_generators(n):
    even, odd = build_basis(n)
    all_gens = even + odd
    assert len(all_gens) == len(set(all_gens)), "Duplicate generators found"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_cartan_count(n):
    even, odd = build_basis(n)
    cartan = [g for g in even if g.startswith("H_")]
    assert len(cartan) == n + 1


@pytest.mark.parametrize("n", [1, 2, 3])
def test_realization_parity_consistency(n):
    even, odd = build_basis(n)
    all_gens = even + odd
    for g in all_gens:
        real = get_realization(g, n)
        expected_p = get_parity(g)
        for coeff, words in real:
            if not words:
                continue
            word_parity = sum(1 for w in words if w.startswith("a_")) % 2
            assert word_parity == expected_p, \
                f"{g}: word parity {word_parity} != generator parity {expected_p}"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema1_json_generated(n):
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    filename = os.path.join(data_dir, f"C_{n}_structure.json")
    assert os.path.exists(filename), f"Missing {filename}"
    with open(filename) as f:
        data = json.load(f)
    assert data["schema_version"] == "5.0"
    assert data["algebra"]["family"] == "C"
    assert data["algebra"]["m"] == 1
    assert data["algebra"]["n"] == n


@pytest.mark.parametrize("n", [1, 2, 3])
def test_structure_constants_parity(n):
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    with open(os.path.join(data_dir, f"C_{n}_structure.json")) as f:
        data = json.load(f)
    parity = data["parity"]
    for sc in data["structure_constants"]:
        pX = parity[sc["X"]]
        pY = parity[sc["Y"]]
        pZ = parity[sc["Z"]]
        assert (pX + pY) % 2 == pZ % 2, \
            f"Parity mismatch: [{sc['X']}, {sc['Y']}] -> {sc['Z']}"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema1_has_central_elements(n):
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    with open(os.path.join(data_dir, f"C_{n}_structure.json")) as f:
        data = json.load(f)
    assert "central_elements" in data
    assert "kappa" in data["central_elements"]
    assert data["central_elements"]["kappa"]["parity"] == 1
    assert "K" in data["central_elements"]
    assert data["central_elements"]["K"]["parity"] == 0
