"""
Unit tests for C(n+1) structure constants generator.
"""

import os
import json
import pytest
from src.C_generators import build_C_structure, get_basis_and_realizations

@pytest.mark.parametrize("n, expected_even, expected_odd, expected_total", [
    (1, 4, 4, 8),
    (2, 11, 8, 19),
    (3, 22, 12, 34),
])
def test_generator_counts_and_dimensions(n, expected_even, expected_odd, expected_total):
    data = build_C_structure(n)
    dim_info = data["algebra"]["dimension"]
    assert dim_info["even"] == expected_even
    assert dim_info["odd"] == expected_odd
    assert dim_info["total"] == expected_total

    even_basis = data["basis"]["even"]
    odd_basis = data["basis"]["odd"]
    assert len(even_basis) == expected_even
    assert len(odd_basis) == expected_odd

    parity_map = data["parity"]
    for name in even_basis:
        assert parity_map[name] == 0
    for name in odd_basis:
        assert parity_map[name] == 1


def test_schema_conformance():
    for n in [1, 2, 3]:
        data = build_C_structure(n)
        assert data["schema_version"] == "5.0"
        assert data["algebra"]["family"] == "C"
        assert data["algebra"]["m"] == 1
        assert "fermions" in data["oscillator_generators"]
        assert "bosons" in data["oscillator_generators"]
        assert "kappa" in data["central_elements"]
        assert "K" in data["central_elements"]
        assert "standard_fermion_anticommutators" in data["oscillator_relations"]


def test_generated_json_files_exist():
    for n in [1, 2, 3]:
        path = f"data/C_{n}_structure.json"
        assert os.path.exists(path)
        with open(path) as f:
            content = json.load(f)
            assert content["algebra"]["n"] == n


def test_specific_bracket_values():
    # Test [E_2del1_p, E_2del1_m] in C(2) (n=1)
    data = build_C_structure(1)
    sc_list = data["structure_constants"]
    
    # Bracket between E_2del1_p and E_2del1_m: should equal 4 * H_2
    found_H2 = False
    for entry in sc_list:
        if entry["X"] == "E_2del1_p" and entry["Y"] == "E_2del1_m":
            if entry["Z"] == "H_2":
                assert entry["coeff"] == "4"
                found_H2 = True
    assert found_H2, "Expected [E_2del1_p, E_2del1_m] = 4 H_2 in C(2)"
