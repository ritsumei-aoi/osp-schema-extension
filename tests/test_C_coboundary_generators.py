import os
import sys
import json
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.C_coboundary_generators import generate_c_coboundary

@pytest.mark.parametrize("n", [1, 2, 3])
def test_coboundary_schema_consistency(n):
    struct_path = f"data/C_{n}_structure.json"
    coboundary_path = f"data/C_{n}_coboundary.json"

    assert os.path.exists(struct_path)
    assert os.path.exists(coboundary_path)

    with open(struct_path, "r") as f:
        s1 = json.load(f)
    with open(coboundary_path, "r") as f:
        s4 = json.load(f)

    # 1. Algebra structure match
    assert s1["algebra"] == s4["algebra"]

    basis_set = set(s1["basis"]["even"] + s1["basis"]["odd"] + ["K"])
    phi_params = set(s4["odd_linear_map_f"]["phi_parameters"].keys())

    # 2. Check coboundary coefficients references
    for entry in s4["coboundary_structure"]["coboundary_coefficients"]:
        assert entry["X"] in basis_set, f"Unknown X in coboundary: {entry['X']}"
        assert entry["Y"] in basis_set, f"Unknown Y in coboundary: {entry['Y']}"
        assert entry["Z"] in basis_set, f"Unknown Z in coboundary: {entry['Z']}"
        assert entry["phi_param"] in phi_params, f"Unknown phi_param in coboundary: {entry['phi_param']}"
