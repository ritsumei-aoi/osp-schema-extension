"""
Unit tests for C(n+1) generator and Schema 1 data.
"""

import json
import os
import pytest
from fractions import Fraction
from src.C_generators import (
    compute_structure_constants,
    build_basis_and_realizations,
    supercommutator
)


@pytest.mark.parametrize("n,expected_even,expected_odd,expected_total", [
    (1, 4, 4, 8),
    (2, 11, 8, 19),
    (3, 22, 12, 34),
])
def test_generator_counts_and_parities(n, expected_even, expected_odd, expected_total):
    even_basis, odd_basis, parity, poly, frappat = build_basis_and_realizations(n)
    assert len(even_basis) == expected_even
    assert len(odd_basis) == expected_odd
    assert len(even_basis) + len(odd_basis) == expected_total

    for gen in even_basis:
        assert parity[gen] == 0
    for gen in odd_basis:
        assert parity[gen] == 1


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema1_json_generation(n):
    filepath = f"data/C_{n}_structure.json"
    assert os.path.exists(filepath), f"{filepath} does not exist"

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["schema_version"] == "5.0"
    assert data["algebra"]["family"] == "C"
    assert data["algebra"]["m"] == 1
    assert data["algebra"]["n"] == n
    assert "central_elements" in data
    assert "kappa" in data["central_elements"]
    assert "K" in data["central_elements"]
    assert "fermions" in data["oscillator_generators"]
    assert "bosons" in data["oscillator_generators"]

    even_dim = 2 * n * n + n + 1
    odd_dim = 4 * n
    total_dim = 2 * n * n + 5 * n + 1
    assert data["algebra"]["dimension"]["even"] == even_dim
    assert data["algebra"]["dimension"]["odd"] == odd_dim
    assert data["algebra"]["dimension"]["total"] == total_dim


@pytest.mark.parametrize("n", [1, 2, 3])
def test_super_antisymmetry(n):
    schema_data, sc_list = compute_structure_constants(n)
    parity = schema_data["parity"]

    # Build bracket lookup table: (X, Y) -> Dict[Z, Fraction]
    bracket_dict = {}
    for entry in sc_list:
        pair = (entry["X"], entry["Y"])
        if pair not in bracket_dict:
            bracket_dict[pair] = {}
        bracket_dict[pair][entry["Z"]] = Fraction(entry["coeff"])

    all_gens = schema_data["basis"]["odd"] + schema_data["basis"]["even"]
    for x in all_gens:
        for y in all_gens:
            px, py = parity[x], parity[y]
            sign = -1 if (px == 1 and py == 1) else 1
            # [Y, X] should equal - sign * [X, Y]
            expected_factor = -sign

            br_xy = bracket_dict.get((x, y), {})
            br_yx = bracket_dict.get((y, x), {})

            # All Z in br_xy must be in br_yx with expected factor
            for z, c in br_xy.items():
                assert z in br_yx, f"Missing [{y}, {x}] bracket for Z={z}"
                assert br_yx[z] == expected_factor * c, f"Antisymmetry failed for [{x}, {y}] vs [{y}, {x}] on {z}"
