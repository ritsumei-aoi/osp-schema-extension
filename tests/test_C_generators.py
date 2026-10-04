import os
import sys
import json
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.C_generators import generate_c_structure, get_basis_and_realizations

@pytest.mark.parametrize("n, expected_even, expected_odd, expected_total", [
    (1, 4, 4, 8),
    (2, 11, 8, 19),
    (3, 22, 12, 34),
])
def test_generator_counts(n, expected_even, expected_odd, expected_total):
    data = generate_c_structure(n)
    even = data["basis"]["even"]
    odd = data["basis"]["odd"]
    dim = data["algebra"]["dimension"]
    
    assert len(even) == expected_even
    assert len(odd) == expected_odd
    assert len(even) + len(odd) == expected_total
    assert dim["even"] == expected_even
    assert dim["odd"] == expected_odd
    assert dim["total"] == expected_total

@pytest.mark.parametrize("n", [1, 2, 3])
def test_parity_assignment(n):
    data = generate_c_structure(n)
    parity = data["parity"]
    even = data["basis"]["even"]
    odd = data["basis"]["odd"]
    
    for g in even:
        assert parity[g] == 0, f"Generator {g} in even basis should have parity 0"
    for g in odd:
        assert parity[g] == 1, f"Generator {g} in odd basis should have parity 1"

@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema_keys(n):
    data = generate_c_structure(n)
    required_keys = [
        "schema_version", "algebra", "oscillator_generators",
        "oscillator_relations", "central_elements", "basis",
        "parity", "generator_realization", "structure_constants", "metadata"
    ]
    for key in required_keys:
        assert key in data, f"Missing required top-level key: {key}"
        
    assert data["algebra"]["family"] == "C"
    assert data["algebra"]["m"] == 1
    assert "kappa" in data["central_elements"]
    assert data["central_elements"]["kappa"]["parity"] == 1
    assert "K" in data["central_elements"]
    assert data["central_elements"]["K"]["parity"] == 0

@pytest.mark.parametrize("n", [1, 2, 3])
def test_json_files_exist_and_valid(n):
    path = f"data/C_{n}_structure.json"
    assert os.path.exists(path), f"JSON file missing: {path}"
    with open(path, "r") as f:
        loaded = json.load(f)
    assert loaded["algebra"]["family"] == "C"
