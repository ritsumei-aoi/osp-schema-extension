import os
import json
import pytest
from fractions import Fraction
from src.C_evaluated import (
    get_default_gb_profile,
    evaluate_gamma,
    generate_evaluated_json,
    save_evaluated_json
)
from src.C_generators import get_basis, get_parity


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema3_generation_and_consistency(n):
    path = os.path.join("data", f"C_{n}_evaluated.json")
    assert os.path.exists(path)
    
    with open(path, "r") as f:
        data = json.load(f)
        
    assert data["schema_version"] == "5.0"
    assert data["algebra"]["family"] == "C"
    assert data["algebra"]["m"] == 1
    assert data["algebra"]["n"] == n
    assert "evaluation" in data
    assert len(data["evaluation"]["parameter_values"]) == 4 * n
    
    # Load Schema 2 to cross-check evaluated sums
    s2_path = os.path.join("data", f"C_{n}_gamma.json")
    with open(s2_path, "r") as f:
        s2 = json.load(f)
        
    s2_map = {}
    for entry in s2["gamma_coefficients"]:
        key = (entry["X"], entry["Y"], entry["Z"])
        p = entry["gb_param"]
        val = Fraction(data["evaluation"]["parameter_values"][p])
        s2_map[key] = s2_map.get(key, Fraction(0)) + Fraction(entry["coeff"]) * val
        
    eval_map = {}
    for entry in data["evaluated_gamma"]:
        key = (entry["X"], entry["Y"], entry["Z"])
        eval_map[key] = Fraction(entry["coeff"])
        
    # Check that non-zero evaluated sums match s2_map exactly
    for key, val in s2_map.items():
        if val != 0:
            assert eval_map.get(key) == val
        else:
            assert key not in eval_map


@pytest.mark.parametrize("n", [1, 2, 3])
def test_evaluated_gamma_antisymmetry(n):
    data = generate_evaluated_json(n)
    parity = data["parity"]
    all_gens = data["basis"]["even"] + data["basis"]["odd"]
    
    eval_map = {}
    for entry in data["evaluated_gamma"]:
        eval_map[(entry["X"], entry["Y"], entry["Z"])] = Fraction(entry["coeff"])
        
    for x in all_gens:
        px = parity[x]
        for y in all_gens:
            py = parity[y]
            sign = -1 if (px * py) % 2 == 1 else 1
            for z in all_gens:
                c_xy = eval_map.get((x, y, z), Fraction(0))
                c_yx = eval_map.get((y, x, z), Fraction(0))
                assert c_yx == -sign * c_xy, f"Evaluated antisymmetry failed for ({x}, {y}, {z})"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_evaluated_gamma_parity(n):
    data = generate_evaluated_json(n)
    parity = data["parity"]
    
    for entry in data["evaluated_gamma"]:
        px = parity[entry["X"]]
        py = parity[entry["Y"]]
        pz = parity[entry["Z"]]
        assert pz == (px + py + 1) % 2
