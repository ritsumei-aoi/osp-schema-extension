"""
test_C_gamma.py: Unit tests for Schema 2 (gamma structure and gb matrix) for C(n+1).
"""

import json
import os
import pytest
from src.C_gamma_generator import get_gb_matrix_info


@pytest.mark.parametrize("n, expected_rows, expected_cols, expected_params", [
    (1, 2, 2, 4),
    (2, 2, 4, 8),
    (3, 2, 6, 12),
])
def test_gb_matrix_dimensions(n, expected_rows, expected_cols, expected_params):
    info = get_gb_matrix_info(n)
    assert info["dimensions"] == [expected_rows, expected_cols]
    assert len(info["parameters"]) == expected_params
    assert info["count"] == expected_params
    assert info["parity"] == 1


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema2_json_consistency(n):
    gamma_path = f"data/C_{n}_gamma.json"
    structure_path = f"data/C_{n}_structure.json"

    assert os.path.exists(gamma_path)
    assert os.path.exists(structure_path)

    with open(gamma_path, "r") as f:
        gdata = json.load(f)
    with open(structure_path, "r") as f:
        sdata = json.load(f)

    # Check basis consistency
    assert gdata["basis"]["even"] == sdata["basis"]["even"]
    assert gdata["basis"]["odd"] == sdata["basis"]["odd"]
    assert gdata["parity"] == sdata["parity"]

    # Check gb_matrix
    assert gdata["gb_matrix"]["count"] == 4 * n
    assert len(gdata["gb_matrix"]["parameters"]) == 4 * n

    # Check inhomogeneous deformation field
    inhom = gdata["inhomogeneous_deformation"]
    assert inhom["total_entries"] == len(inhom["gamma_coefficients"])
    assert inhom["total_entries"] > 0

    # Check graded skew-symmetry across all gamma entries
    parities = gdata["parity"]
    brackets = {}
    for entry in inhom["gamma_coefficients"]:
        key = (entry["X"], entry["Y"], entry["Z"], entry["param"])
        brackets[key] = int(entry["coeff"]) if "/" not in entry["coeff"] else float(entry["coeff"])

    all_pairs = set((entry["X"], entry["Y"]) for entry in inhom["gamma_coefficients"])
    for X, Y in all_pairs:
        pX = parities[X]
        pY = parities[Y]
        expected_sign = - ((-1)**(pX * pY))

        for entry in inhom["gamma_coefficients"]:
            if entry["X"] == X and entry["Y"] == Y:
                Z = entry["Z"]
                param = entry["param"]
                c_XY = brackets.get((X, Y, Z, param), 0)
                c_YX = brackets.get((Y, X, Z, param), 0)
                assert c_YX == expected_sign * c_XY, f"Skew-symmetry failed in gamma for ({X}, {Y}) -> {Z}, param {param}"
