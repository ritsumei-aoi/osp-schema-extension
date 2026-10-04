"""
Unit tests for C_coboundary.py (Schema 4 / Layer 4).
"""

import os
import json
import pytest
from src.C_coboundary import compute_coboundary_structure, generate_all_coboundary_files


@pytest.mark.parametrize("n,expected_map_count", [
    (1, 32),
    (2, 176),
    (3, 528),
])
def test_coboundary_map_count(n, expected_map_count):
    data = compute_coboundary_structure(n)
    assert len(data["odd_map_basis"]) == expected_map_count
    assert len(data["coboundary_coefficients"]) > 0


@pytest.mark.parametrize("n", [1, 2, 3])
def test_coboundary_parity_consistency(n):
    data = compute_coboundary_structure(n)
    parity = data["parity"]

    # In coboundary term (delta f)(X, Y) -> Z with map f: source -> target:
    # p(target) = 1 - p(source)
    # Total parity of delta f is odd: p(Z) = (p(X) + p(Y) + 1) % 2
    for entry in data["coboundary_coefficients"]:
        X = entry["X"]
        Y = entry["Y"]
        Z = entry["Z"]
        pX = parity[X]
        pY = parity[Y]
        pZ = parity[Z]
        assert pZ == (pX + pY + 1) % 2, f"Parity mismatch in coboundary for [{X}, {Y}] -> {Z}"


def test_generate_all_coboundary_files():
    generate_all_coboundary_files("data")
    for n in [1, 2, 3]:
        filepath = os.path.join("data", f"C_{n}_coboundary.json")
        assert os.path.exists(filepath)
        with open(filepath, "r") as f:
            data = json.load(f)
            assert data["algebra"]["n"] == n
            assert len(data["coboundary_coefficients"]) > 0
