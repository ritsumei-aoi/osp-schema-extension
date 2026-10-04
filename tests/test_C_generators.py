"""
Unit tests for C_generators.py
"""

import os
import json
import pytest
from fractions import Fraction
from src.C_generators import (
    build_basis_and_generators,
    compute_structure_constants,
    generate_c_structure_json,
    generate_all_files,
)


@pytest.mark.parametrize("n,expected_even,expected_odd,expected_total", [
    (1, 4, 4, 8),
    (2, 11, 8, 19),
    (3, 22, 12, 34),
])
def test_generator_counts_and_parities(n, expected_even, expected_odd, expected_total):
    even_basis, odd_basis, parity, gen_poly = build_basis_and_generators(n)
    assert len(even_basis) == expected_even
    assert len(odd_basis) == expected_odd
    assert len(even_basis) + len(odd_basis) == expected_total

    for g in even_basis:
        assert parity[g] == 0
    for g in odd_basis:
        assert parity[g] == 1


@pytest.mark.parametrize("n", [1, 2, 3])
def test_bracket_graded_skew_symmetry(n):
    even_basis, odd_basis, parity, _, structure_constants, bracket_dict = compute_structure_constants(n)
    all_gens = even_basis + odd_basis

    # Verify [Y, X, Z] == - (-1)^{p(X)p(Y)} [X, Y, Z]
    for X in all_gens:
        for Y in all_gens:
            pX = parity[X]
            pY = parity[Y]
            pXY = (-1) ** (pX * pY)
            for Z in all_gens:
                c_XY = bracket_dict.get((X, Y, Z), Fraction(0))
                c_YX = bracket_dict.get((Y, X, Z), Fraction(0))
                assert c_YX == - pXY * c_XY, f"Skew-symmetry failed for [{X}, {Y}] vs [{Y}, {X}] on {Z}"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema_conformance(n, tmp_path):
    data = generate_c_structure_json(n)
    assert data["schema_version"] == "5.0"
    assert data["algebra"]["family"] == "C"
    assert data["algebra"]["m"] == 1
    assert data["algebra"]["n"] == n
    assert data["algebra"]["dimension"]["even"] == 2 * n**2 + n + 1
    assert data["algebra"]["dimension"]["odd"] == 4 * n
    assert "central_elements" in data
    assert "kappa" in data["central_elements"]
    assert "K" in data["central_elements"]
    assert "standard_fermion_anticommutators" in data["oscillator_relations"]
    assert "realizations" in data["generator_realization"]
    assert len(data["structure_constants"]) > 0


def test_generate_all_files():
    generate_all_files("data")
    for n in [1, 2, 3]:
        filepath = os.path.join("data", f"C_{n}_structure.json")
        assert os.path.exists(filepath)
        with open(filepath, "r") as f:
            data = json.load(f)
            assert data["algebra"]["n"] == n
