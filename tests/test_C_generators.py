import pytest
import json
import os

def test_json_files_exist():
    for n in [1, 2, 3]:
        assert os.path.exists(f"data/C_{n}_structure.json")

def test_dimensions():
    for n in [1, 2, 3]:
        with open(f"data/C_{n}_structure.json") as f:
            data = json.load(f)
            
        expected_even = 2 * n**2 + n + 1
        expected_odd = 4 * n
        expected_total = expected_even + expected_odd
        
        assert data["algebra"]["dimension"]["even"] == expected_even
        assert data["algebra"]["dimension"]["odd"] == expected_odd
        assert data["algebra"]["dimension"]["total"] == expected_total
        
        assert len(data["basis"]["even"]) == expected_even
        assert len(data["basis"]["odd"]) == expected_odd
        
        # Verify parities
        for gen in data["basis"]["even"]:
            assert data["parity"][gen] == 0
        for gen in data["basis"]["odd"]:
            assert data["parity"][gen] == 1

def test_central_elements():
    for n in [1, 2, 3]:
        with open(f"data/C_{n}_structure.json") as f:
            data = json.load(f)
            
        assert "kappa" in data["central_elements"]
        assert "K" in data["central_elements"]
        assert data["central_elements"]["kappa"]["parity"] == 1
        assert data["central_elements"]["K"]["parity"] == 0
