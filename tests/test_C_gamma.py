"""
test_C_gamma.py: Unit tests for Schema 2 (gamma structure) for C(n+1).
Tests gb_matrix dimensions, consistency with Schema 1, and parity properties of gamma.
"""

import json
import os
import pytest
from src.C_gamma import get_gb_matrix_info


@pytest.mark.parametrize("n, expected_params", [
    (1, 4),
    (2, 8),
    (3, 12),
])
def test_gb_matrix_dimensions(n, expected_params):
    info = get_gb_matrix_info(n)
    assert info["shape"] == [2, 2 * n]
    assert info["total_parameters"] == expected_params
    assert len(info["parameters"]) == expected_params
    assert len(info["rows"]) == 2
    assert len(info["columns"]) == 2 * n


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema2_consistency_with_schema1(n):
    path1 = os.path.join("data", f"C_{n}_structure.json")
    path2 = os.path.join("data", f"C_{n}_gamma.json")
    assert os.path.exists(path1)
    assert os.path.exists(path2)

    with open(path1, "r", encoding="utf-8") as f:
        s1 = json.load(f)
    with open(path2, "r", encoding="utf-8") as f:
        s2 = json.load(f)

    # Check identical algebra metadata
    assert s1["algebra"] == s2["algebra"]
    # Check identical basis
    assert s1["basis"] == s2["basis"]
    # Check identical parities
    assert s1["parity"] == s2["parity"]


@pytest.mark.parametrize("n", [1, 2, 3])
def test_gamma_parity_grading(n):
    path2 = os.path.join("data", f"C_{n}_gamma.json")
    with open(path2, "r", encoding="utf-8") as f:
        s2 = json.load(f)

    parities = s2["parity"]
    for term in s2["inhomogeneous_deformation"]["gamma_terms"]:
        p_x = parities[term["X"]]
        p_y = parities[term["Y"]]
        p_z = parities[term["Z"]]
        # Since kappa has parity 1, gamma(X, Y) must satisfy p(Z) = (p(X) + p(Y) + 1) mod 2
        expected_pz = (p_x + p_y + 1) % 2
        assert p_z == expected_pz, (
            f"Gamma term ({term['X']}, {term['Y']} -> {term['Z']}) violates parity condition! "
            f"p(X)={p_x}, p(Y)={p_y}, p(Z)={p_z}, expected={expected_pz}"
        )
