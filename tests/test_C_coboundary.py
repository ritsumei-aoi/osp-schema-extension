import os
import json
import pytest

@pytest.mark.parametrize("n,expected_dim_even,expected_dim_odd,expected_map_dim", [
    (1, 4, 4, 32),
    (2, 11, 8, 176),
    (3, 22, 12, 528),
])
def test_coboundary_json_structure(n, expected_dim_even, expected_dim_odd, expected_map_dim):
    path = f"data/C_{n}_coboundary.json"
    assert os.path.exists(path), f"{path} does not exist"
    
    with open(path, "r") as f:
        data = json.load(f)
        
    assert data["schema_version"] == "5.0"
    assert data["algebra"]["family"] == "C"
    assert data["algebra"]["m"] == 1
    assert data["algebra"]["n"] == n
    assert data["algebra"]["dimension"]["even"] == expected_dim_even
    assert data["algebra"]["dimension"]["odd"] == expected_dim_odd
    assert data["odd_linear_map_space"]["total_dimension"] == expected_map_dim
    assert len(data["odd_linear_map_space"]["parameters"]) == expected_map_dim
    
    assert "coboundary_operator" in data
    assert "coboundary_coefficients" in data["coboundary_operator"]
    assert len(data["coboundary_operator"]["coboundary_coefficients"]) > 0

def test_coboundary_parity_and_antisymmetry():
    # Test on C_1
    with open("data/C_1_coboundary.json", "r") as f:
        data = json.load(f)
        
    parity = data["parity"]
    coeffs = data["coboundary_operator"]["coboundary_coefficients"]
    
    # Check parity condition: p(Z) = (p(X) + p(Y) + 1) mod 2
    for term in coeffs:
        px = parity[term["X"]]
        py = parity[term["Y"]]
        pz = parity[term["Z"]]
        assert pz == (px + py + 1) % 2, f"Parity mismatch in term {term}"
        
    # Check graded antisymmetry: (delta f)(Y, X) = -(-1)^{p(X)p(Y)} (delta f)(X, Y)
    # Collect map: (X, Y, Z, phi) -> coeff
    val_map = {}
    for term in coeffs:
        val_map[(term["X"], term["Y"], term["Z"], term["phi"])] = int(term["coeff"])
        
    for (x, y, z, phi), coeff in val_map.items():
        px = parity[x]
        py = parity[y]
        expected_opp = - ((-1)**(px * py)) * coeff
        opp = val_map.get((y, x, z, phi), 0)
        assert opp == expected_opp, f"Antisymmetry failed for {x}, {y}, {z}, {phi}: {opp} != {expected_opp}"
