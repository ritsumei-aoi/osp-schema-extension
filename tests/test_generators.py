import json
import os
import pytest

def test_json_schemas():
    for n in [1, 2, 3]:
        with open(f"data/C_{n}_structure.json") as f:
            data = json.load(f)
            assert data["schema_version"] == "5.0"
            assert data["algebra"]["family"] == "C"
            assert data["algebra"]["m"] == 1
            assert data["algebra"]["n"] == n
            
            # Check dimension counts
            even_dim = 2*n*n + n + 1
            odd_dim = 4*n
            assert data["algebra"]["dimension"]["even"] == even_dim
            assert data["algebra"]["dimension"]["odd"] == odd_dim
            assert len(data["basis"]["even"]) == even_dim
            assert len(data["basis"]["odd"]) == odd_dim
            
            # Check parity assignments
            for k in data["basis"]["even"]:
                assert data["parity"][k] == 0
            for k in data["basis"]["odd"]:
                assert data["parity"][k] == 1
