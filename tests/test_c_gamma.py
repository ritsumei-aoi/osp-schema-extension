import os
import json
import pytest
from fractions import Fraction
from src.C_gamma import (
    get_gb_matrix,
    compute_gamma_coefficients,
    generate_gamma_json,
    save_gamma_json
)
from src.C_generators import get_basis, get_parity


@pytest.mark.parametrize("n, expected_params", [
    (1, 4),
    (2, 8),
    (3, 12),
])
def test_gb_matrix_dimensions(n, expected_params):
    gb_info = get_gb_matrix(n)
    assert gb_info["dimensions"]["rows"] == 2
    assert gb_info["dimensions"]["cols"] == 2 * n
    assert gb_info["dimensions"]["total_parameters"] == expected_params
    assert len(gb_info["parameter_list"]) == expected_params
    assert len(gb_info["matrix"]) == 2
    assert len(gb_info["matrix"][0]) == 2 * n
    assert len(gb_info["matrix"][1]) == 2 * n


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema1_schema2_consistency(n):
    # Check that basis, algebra, and parity match between Schema 1 and Schema 2
    s1_path = os.path.join("data", f"C_{n}_structure.json")
    s2_path = os.path.join("data", f"C_{n}_gamma.json")
    
    assert os.path.exists(s1_path)
    assert os.path.exists(s2_path)
    
    with open(s1_path, "r") as f:
        s1 = json.load(f)
    with open(s2_path, "r") as f:
        s2 = json.load(f)
        
    assert s1["schema_version"] == s2["schema_version"]
    assert s1["algebra"] == s2["algebra"]
    assert s1["basis"] == s2["basis"]
    assert s1["parity"] == s2["parity"]


@pytest.mark.parametrize("n", [1, 2])
def test_gamma_graded_antisymmetry(n):
    gamma_coeffs = compute_gamma_coefficients(n)
    parity = get_parity(n)
    basis = get_basis(n)
    all_gens = basis["even"] + basis["odd"]
    
    # Map (X, Y, Z, param) -> Fraction
    gamma_map = {}
    for entry in gamma_coeffs:
        key = (entry["X"], entry["Y"], entry["Z"], entry["gb_param"])
        gamma_map[key] = Fraction(entry["coeff"])
        
    for x in all_gens:
        px = parity[x]
        for y in all_gens:
            py = parity[y]
            sign = -1 if (px * py) % 2 == 1 else 1
            for z in all_gens:
                for r in ["a_1_p", "a_1_m"]:
                    for j in range(1, n + 1):
                        for s in ["p", "m"]:
                            param = f"gb_{r}_b_{j}_{s}"
                            c_xy = gamma_map.get((x, y, z, param), Fraction(0))
                            c_yx = gamma_map.get((y, x, z, param), Fraction(0))
                            assert c_yx == -sign * c_xy, f"Antisymmetry failed for ({x}, {y}, {z}, {param})"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_gamma_parity_grading(n):
    gamma_coeffs = compute_gamma_coefficients(n)
    parity = get_parity(n)
    
    for entry in gamma_coeffs:
        px = parity[entry["X"]]
        py = parity[entry["Y"]]
        pz = parity[entry["Z"]]
        # Because kappa is odd (p=1), p(kappa * Z) = 1 + pz
        # Total parity requires (1 + pz) == (px + py) mod 2, so pz == (px + py + 1) mod 2
        assert pz == (px + py + 1) % 2, f"Parity mismatch in entry: {entry}"
