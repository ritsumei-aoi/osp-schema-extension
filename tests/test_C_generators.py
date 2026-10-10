import json
import os
import pytest

def test_json_files_exist():
    for n in [1, 2, 3]:
        assert os.path.exists(f"data/C_{n}_structure.json")

def test_schema_structure():
    with open("data/C_1_structure.json") as f:
        data = json.load(f)
    
    assert data["schema_version"] == "5.0"
    assert data["algebra"]["family"] == "C"
    assert data["algebra"]["m"] == 1
    assert data["algebra"]["n"] == 1
    
    assert "kappa" in data["central_elements"]
    assert "K" in data["central_elements"]
    assert data["central_elements"]["kappa"]["parity"] == 1
    assert data["central_elements"]["K"]["parity"] == 0

def test_basis_lengths():
    with open("data/C_2_structure.json") as f:
        data = json.load(f)
    
    n = 2
    even_len = 2*n**2 + n + 1
    odd_len = 4*n
    
    assert len(data["basis"]["even"]) == even_len
    assert len(data["basis"]["odd"]) == odd_len

def test_structure_constants_valid():
    with open("data/C_1_structure.json") as f:
        data = json.load(f)
    
    for sc in data["structure_constants"]:
        assert "X" in sc
        assert "Y" in sc
        assert "Z" in sc
        assert "coeff" in sc
        
        # Verify parities match Z parity
        px = data["parity"][sc["X"]]
        py = data["parity"][sc["Y"]]
        pz = data["parity"][sc["Z"]]
        assert (px + py) % 2 == pz
