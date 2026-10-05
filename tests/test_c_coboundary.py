import os
import json
import pytest
from fractions import Fraction
from src.C_coboundary import (
    get_f_map_info,
    compute_coboundary_coefficients,
    generate_coboundary_json,
    save_coboundary_json
)
from src.C_generators import get_basis, get_parity


@pytest.mark.parametrize("n, expected_d0, expected_d1, expected_params", [
    (1, 4, 4, 32),
    (2, 11, 8, 176),
    (3, 22, 12, 528),
])
def test_f_map_dimensions(n, expected_d0, expected_d1, expected_params):
    f_info = get_f_map_info(n)
    assert f_info["even_dim"] == expected_d0
    assert f_info["odd_dim"] == expected_d1
    assert f_info["total_parameters"] == expected_params
    assert len(f_info["parameter_list"]) == expected_params


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema1_schema4_consistency(n):
    s1_path = os.path.join("data", f"C_{n}_structure.json")
    s4_path = os.path.join("data", f"C_{n}_coboundary.json")
    assert os.path.exists(s1_path)
    assert os.path.exists(s4_path)
    
    with open(s1_path, "r") as f:
        s1 = json.load(f)
    with open(s4_path, "r") as f:
        s4 = json.load(f)
        
    assert s1["schema_version"] == s4["schema_version"]
    assert s1["algebra"] == s4["algebra"]
    assert s1["basis"] == s4["basis"]
    assert s1["parity"] == s4["parity"]


@pytest.mark.parametrize("n", [1, 2])
def test_coboundary_graded_antisymmetry(n):
    coeffs = compute_coboundary_coefficients(n)
    parity = get_parity(n)
    basis = get_basis(n)
    all_gens = basis["even"] + basis["odd"]
    
    coeff_map = {}
    for entry in coeffs:
        key = (entry["X"], entry["Y"], entry["Z"], entry["f_param"])
        coeff_map[key] = Fraction(entry["coeff"])
        
    f_info = get_f_map_info(n)
    all_params = f_info["parameter_list"]
    
    for x in all_gens:
        px = parity[x]
        for y in all_gens:
            py = parity[y]
            sign = -1 if (px * py) % 2 == 1 else 1
            for z in all_gens:
                for param in all_params:
                    c_xy = coeff_map.get((x, y, z, param), Fraction(0))
                    c_yx = coeff_map.get((y, x, z, param), Fraction(0))
                    if c_xy != 0 or c_yx != 0:
                        assert c_yx == -sign * c_xy, f"Antisymmetry failed for ({x}, {y}, {z}, {param})"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_coboundary_parity_grading(n):
    coeffs = compute_coboundary_coefficients(n)
    parity = get_parity(n)
    
    for entry in coeffs:
        px = parity[entry["X"]]
        py = parity[entry["Y"]]
        pz = parity[entry["Z"]]
        # Parity of delta(f)(X, Y) is (px + py + 1) mod 2 because f is an odd map
        assert pz == (px + py + 1) % 2, f"Parity mismatch in entry: {entry}"
