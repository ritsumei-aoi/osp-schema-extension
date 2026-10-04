import os
import sys
import json
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.C_gamma_generators import generate_c_gamma

@pytest.mark.parametrize("n, expected_gb_count", [
    (1, 4),
    (2, 8),
    (3, 12),
])
def test_gb_matrix_size(n, expected_gb_count):
    data = generate_c_gamma(n)
    gb_matrix = data["gb_matrix"]
    assert gb_matrix["parameter_count"] == expected_gb_count
    assert len(gb_matrix["parameters"]) == expected_gb_count

@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema1_and_schema2_consistency(n):
    struct_path = f"data/C_{n}_structure.json"
    gamma_path = f"data/C_{n}_gamma.json"
    
    assert os.path.exists(struct_path)
    assert os.path.exists(gamma_path)

    with open(struct_path, "r") as f:
        s1 = json.load(f)
    with open(gamma_path, "r") as f:
        s2 = json.load(f)

    # 1. Algebra dimension consistency
    assert s1["algebra"] == s2["algebra"]

    basis_set = set(s1["basis"]["even"] + s1["basis"]["odd"] + ["K"])
    gb_params = set(s2["gb_matrix"]["parameters"].keys())

    # 2. Check gamma coefficients references
    for entry in s2["inhomogeneous_deformation"]["gamma_coefficients"]:
        assert entry["X"] in basis_set, f"Unknown X in gamma: {entry['X']}"
        assert entry["Y"] in basis_set, f"Unknown Y in gamma: {entry['Y']}"
        assert entry["Z"] in basis_set, f"Unknown Z in gamma: {entry['Z']}"
        assert entry["gb_param"] in gb_params, f"Unknown gb_param in gamma: {entry['gb_param']}"
