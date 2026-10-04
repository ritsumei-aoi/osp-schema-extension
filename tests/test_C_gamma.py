"""
Unit tests for C_gamma.py (Schema 2: Inhomogeneous deformation).
"""

import os
import json
import pytest
from src.C_gamma import compute_gamma_structure, generate_all_gamma_files


@pytest.mark.parametrize("n,expected_gb_count", [
    (1, 4),
    (2, 8),
    (3, 12),
])
def test_gb_matrix_structure(n, expected_gb_count):
    data = compute_gamma_structure(n)
    gb_matrix = data["gb_matrix"]
    assert gb_matrix["dimensions"] == [2, 2 * n]
    assert gb_matrix["count"] == expected_gb_count
    assert len(gb_matrix["parameters"]) == expected_gb_count


@pytest.mark.parametrize("n", [1, 2, 3])
def test_gamma_parity_consistency(n):
    data = compute_gamma_structure(n)
    parity = dict(data["parity"])
    parity["K"] = 0  # K is even central element

    # Deformation preserves total parity with p(kappa) = 1:
    # p(Z) = (p(X) + p(Y) + 1) % 2
    for entry in data["gamma_coefficients"]:
        X = entry["X"]
        Y = entry["Y"]
        Z = entry["Z"]
        pX = parity[X]
        pY = parity[Y]
        pZ = parity[Z]
        assert pZ == (pX + pY + 1) % 2, f"Parity mismatch in gamma for [{X}, {Y}] -> {Z}: pX={pX}, pY={pY}, pZ={pZ}"


def test_generate_all_gamma_files():
    generate_all_gamma_files("data")
    for n in [1, 2, 3]:
        filepath = os.path.join("data", f"C_{n}_gamma.json")
        assert os.path.exists(filepath)
        with open(filepath, "r") as f:
            data = json.load(f)
            assert data["gb_matrix"]["count"] == 4 * n
            assert len(data["gamma_coefficients"]) > 0
