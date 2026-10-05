"""Unit tests for C(n+1) generator script, basis dimensions, parities, and Schema 1 JSON."""

import json
import os
import pytest
from src.C_generators import (
    build_basis,
    build_generator_realizations,
    compute_structure_constants,
    generate_all_schema_1
)

@pytest.mark.parametrize("n,expected_even,expected_odd,expected_total", [
    (1, 4, 4, 8),
    (2, 11, 8, 19),
    (3, 22, 12, 34)
])
def test_generator_counts(n, expected_even, expected_odd, expected_total):
    even_basis, odd_basis = build_basis(n)
    assert len(even_basis) == expected_even
    assert len(odd_basis) == expected_odd
    assert len(even_basis) + len(odd_basis) == expected_total

@pytest.mark.parametrize("n", [1, 2, 3])
def test_generator_parities(n):
    even_basis, odd_basis = build_basis(n)
    polys, parities, realizations = build_generator_realizations(n)
    
    for gen in even_basis:
        assert parities[gen] == 0, f"Even generator {gen} has incorrect parity {parities[gen]}"
    for gen in odd_basis:
        assert parities[gen] == 1, f"Odd generator {gen} has incorrect parity {parities[gen]}"

@pytest.mark.parametrize("n", [1, 2, 3])
def test_structure_constants_parity_conservation(n):
    sc_list, schema_1 = compute_structure_constants(n)
    parities = schema_1["parity"]
    
    for entry in sc_list:
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        p_x = parities[x]
        p_y = parities[y]
        p_z = parities[z]
        assert (p_x + p_y) % 2 == p_z, (
            f"Parity violation in [{x}, {y}] = ... + {entry['coeff']} * {z}: "
            f"p({x})={p_x}, p({y})={p_y}, p({z})={p_z}"
        )

@pytest.mark.parametrize("n", [1, 2, 3])
def test_graded_antisymmetry(n):
    sc_list, schema_1 = compute_structure_constants(n)
    parities = schema_1["parity"]
    
    from fractions import Fraction
    sc_dict = {}
    for entry in sc_list:
        sc_dict[(entry["X"], entry["Y"], entry["Z"])] = Fraction(entry["coeff"])
        
    basis = schema_1["basis"]["even"] + schema_1["basis"]["odd"]
    for x in basis:
        for y in basis:
            p_xy = (-1) ** (parities[x] * parities[y])
            for z in basis:
                c_xy = sc_dict.get((x, y, z), Fraction(0))
                c_yx = sc_dict.get((y, x, z), Fraction(0))
                # [X, Y} = - (-1)^{p(X)p(Y)} [Y, X}
                assert c_xy == - p_xy * c_yx, (
                    f"Graded antisymmetry violation for [{x}, {y}] vs [{y}, {x}] on {z}: "
                    f"c_xy={c_xy}, c_yx={c_yx}, p_xy={p_xy}"
                )

@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema_1_file_conformance(n):
    filepath = os.path.join("data", f"C_{n}_structure.json")
    assert os.path.exists(filepath), f"Missing data file {filepath}"
    
    with open(filepath, "r") as f:
        data = json.load(f)
        
    assert data["schema_version"] == "5.0"
    assert data["algebra"]["family"] == "C"
    assert data["algebra"]["m"] == 1
    assert data["algebra"]["n"] == n
    assert data["algebra"]["cartan_type"] == f"C({n+1})"
    assert "kappa" in data["central_elements"]
    assert "K" in data["central_elements"]
    assert data["central_elements"]["kappa"]["parity"] == 1
    assert data["central_elements"]["K"]["parity"] == 0
    assert "fermions" in data["oscillator_generators"]
    assert "bosons" in data["oscillator_generators"]
    assert len(data["oscillator_generators"]["fermions"]["labels"]) == 2
    assert len(data["oscillator_generators"]["bosons"]["labels"]) == 2 * n
