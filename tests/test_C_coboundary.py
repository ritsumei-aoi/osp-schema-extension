"""
Unit tests for C(n+1) Schema 4 (coboundary structure) generator.
"""

from fractions import Fraction
import json
import os
import pytest
from src.C_coboundary_generators import compute_coboundary_structure


@pytest.mark.parametrize("n,expected_phi_dim", [
    (1, 32),
    (2, 176),
    (3, 528),
])
def test_coboundary_map_f_dimension(n, expected_phi_dim):
    with open(os.path.join("data", f"C_{n}_coboundary.json"), "r", encoding="utf-8") as f:
        s4 = json.load(f)
    assert s4["schema_version"] == "5.0"
    assert s4["map_f"]["dimension"] == expected_phi_dim
    assert len(s4["map_f"]["parameters"]) == expected_phi_dim


@pytest.mark.parametrize("n", [1, 2, 3])
def test_coboundary_graded_antisymmetry(n):
    with open(os.path.join("data", f"C_{n}_structure.json"), "r", encoding="utf-8") as f:
        s1 = json.load(f)
    parity = s1["parity"]
    all_generators = s1["basis"]["odd"] + s1["basis"]["even"]

    with open(os.path.join("data", f"C_{n}_coboundary.json"), "r", encoding="utf-8") as f:
        s4 = json.load(f)

    # Table: (phi_param, X, Y, Z) -> coeff
    delta_table = {}
    for item in s4["coboundary_structure"]["terms"]:
        p = item["phi_param"]
        x, y, z = item["X"], item["Y"], item["Z"]
        c = Fraction(item["coeff"])
        delta_table[(p, x, y, z)] = c

    # Sample test across first 10 parameters to ensure rapid test execution while validating parity
    test_params = s4["map_f"]["parameters"][:10]
    for p in test_params:
        for x in all_generators:
            for y in all_generators:
                sign = -1 if (parity[x] == 1 and parity[y] == 1) else 1
                for z in all_generators:
                    c_xy = delta_table.get((p, x, y, z), Fraction(0))
                    c_yx = delta_table.get((p, y, x, z), Fraction(0))
                    assert c_yx == -sign * c_xy, f"Coboundary graded antisymmetry failed for {p}, ({x}, {y}) -> {z}"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema_4_consistency_with_schema_1(n):
    with open(os.path.join("data", f"C_{n}_structure.json"), "r", encoding="utf-8") as f:
        s1 = json.load(f)
    with open(os.path.join("data", f"C_{n}_coboundary.json"), "r", encoding="utf-8") as f:
        s4 = json.load(f)

    assert s1["schema_version"] == s4["schema_version"]
    assert s1["algebra"] == s4["algebra"]
