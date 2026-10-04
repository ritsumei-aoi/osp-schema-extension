"""
Unit tests for C(n+1) Schema 2 (gamma structure) generator.
"""

from fractions import Fraction
import json
import os
import pytest
from src.C_gamma_generators import compute_gamma_structure, get_gb_params


@pytest.mark.parametrize("n,expected_params_count", [
    (1, 4),
    (2, 8),
    (3, 12),
])
def test_gb_parameters_count_and_shape(n, expected_params_count):
    params = get_gb_params(n)
    assert len(params) == expected_params_count
    _, schema = compute_gamma_structure(n)
    assert schema["gb_matrix"]["count"] == expected_params_count
    assert schema["gb_matrix"]["shape"] == [2, 2 * n]


@pytest.mark.parametrize("n", [1, 2, 3])
def test_gamma_graded_antisymmetry(n):
    with open(os.path.join("data", f"C_{n}_structure.json"), "r", encoding="utf-8") as f:
        struct_data = json.load(f)
    parity = struct_data["parity"]
    all_generators = struct_data["basis"]["odd"] + struct_data["basis"]["even"]

    with open(os.path.join("data", f"C_{n}_gamma.json"), "r", encoding="utf-8") as f:
        gamma_data = json.load(f)

    # Table: (param, X, Y, Z) -> coeff
    gamma_table = {}
    for item in gamma_data["inhomogeneous_deformation"]["gamma_structure"]:
        p = item["gb_param"]
        x, y, z = item["X"], item["Y"], item["Z"]
        c = Fraction(item["coeff"])
        gamma_table[(p, x, y, z)] = c

    for p in gamma_data["gb_matrix"]["parameters"]:
        for x in all_generators:
            for y in all_generators:
                sign = -1 if (parity[x] == 1 and parity[y] == 1) else 1
                for z in all_generators:
                    c_xy = gamma_table.get((p, x, y, z), Fraction(0))
                    c_yx = gamma_table.get((p, y, x, z), Fraction(0))
                    assert c_yx == -sign * c_xy, f"Gamma antisymmetry failed for {p}, ({x}, {y}) -> {z}"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema_2_consistency_with_schema_1(n):
    with open(os.path.join("data", f"C_{n}_structure.json"), "r", encoding="utf-8") as f:
        s1 = json.load(f)
    with open(os.path.join("data", f"C_{n}_gamma.json"), "r", encoding="utf-8") as f:
        s2 = json.load(f)

    assert s1["schema_version"] == s2["schema_version"]
    assert s1["algebra"] == s2["algebra"]
