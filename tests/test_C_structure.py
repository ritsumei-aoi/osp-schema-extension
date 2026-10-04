"""
test_C_structure.py: Unit tests for C(n+1) basis, parities, dimensions, and Schema 1 JSONs.
"""

import json
import os
import pytest
from src.C_generators import get_basis_lists, get_generator_operators, generate_schema1_json


@pytest.mark.parametrize("n, expected_even, expected_odd, expected_total", [
    (1, 4, 4, 8),
    (2, 11, 8, 19),
    (3, 22, 12, 34),
])
def test_generator_counts_and_dimensions(n, expected_even, expected_odd, expected_total):
    even_basis, odd_basis = get_basis_lists(n)
    assert len(even_basis) == expected_even
    assert len(odd_basis) == expected_odd
    assert len(even_basis) + len(odd_basis) == expected_total

    # Theoretical formulas
    assert expected_even == 2 * n**2 + n + 1
    assert expected_odd == 4 * n
    assert expected_total == 2 * n**2 + 5 * n + 1


@pytest.mark.parametrize("n", [1, 2, 3])
def test_parities_and_realizations(n):
    gens, parities, realizations = get_generator_operators(n)
    even_basis, odd_basis = get_basis_lists(n)

    for gen in even_basis:
        assert parities[gen] == 0
        assert realizations[gen]["parity"] == 0

    for gen in odd_basis:
        assert parities[gen] == 1
        assert realizations[gen]["parity"] == 1

    # Check cartan counts
    cartan_gens = [g for g in even_basis if g.startswith("H_")]
    assert len(cartan_gens) == n + 1


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema1_json_structure(n):
    filepath = f"data/C_{n}_structure.json"
    assert os.path.exists(filepath), f"{filepath} does not exist"

    with open(filepath, "r") as f:
        data = json.load(f)

    # Check top-level keys
    required_keys = [
        "schema_version", "algebra", "central_elements", "oscillator_generators",
        "oscillator_relations", "basis", "parity", "generator_realization",
        "structure_constants", "metadata"
    ]
    for k in required_keys:
        assert k in data, f"Missing key {k} in {filepath}"

    # Check algebra metadata
    assert data["algebra"]["family"] == "C"
    assert data["algebra"]["m"] == 1
    assert data["algebra"]["n"] == n
    assert data["algebra"]["cartan_type"] == f"C({n+1})"
    assert data["algebra"]["dimension"]["even"] == 2 * n**2 + n + 1
    assert data["algebra"]["dimension"]["odd"] == 4 * n

    # Check central elements
    assert "kappa" in data["central_elements"]
    assert data["central_elements"]["kappa"]["parity"] == 1
    assert "K" in data["central_elements"]
    assert data["central_elements"]["K"]["parity"] == 0

    # Check oscillator generators
    assert "fermions" in data["oscillator_generators"]
    assert data["oscillator_generators"]["fermions"]["m"] == 1
    assert data["oscillator_generators"]["fermions"]["labels"] == ["a_1_p", "a_1_m"]
    assert "bosons" in data["oscillator_generators"]
    assert data["oscillator_generators"]["bosons"]["count"] == 2 * n

    # Check structure constants format
    assert len(data["structure_constants"]) > 0
    for entry in data["structure_constants"]:
        assert "X" in entry and "Y" in entry and "Z" in entry
        assert "coeff" in entry and "sign_rule" in entry


@pytest.mark.parametrize("n", [1, 2, 3])
def test_graded_skew_symmetry(n):
    filepath = f"data/C_{n}_structure.json"
    with open(filepath, "r") as f:
        data = json.load(f)

    parities = data["parity"]
    brackets = {}
    for entry in data["structure_constants"]:
        key = (entry["X"], entry["Y"], entry["Z"])
        brackets[key] = int(entry["coeff"]) if "/" not in entry["coeff"] else float(entry["coeff"])

    # For every pair (X, Y) with non-zero [X, Y}, check [Y, X} = - (-1)^{p(X)p(Y)} [X, Y}
    all_pairs = set((entry["X"], entry["Y"]) for entry in data["structure_constants"])
    for X, Y in all_pairs:
        pX = parities[X]
        pY = parities[Y]
        expected_sign = - ((-1)**(pX * pY))

        # Check all Z
        for entry in data["structure_constants"]:
            if entry["X"] == X and entry["Y"] == Y:
                Z = entry["Z"]
                c_XY = brackets.get((X, Y, Z), 0)
                c_YX = brackets.get((Y, X, Z), 0)
                assert c_YX == expected_sign * c_XY, f"Skew-symmetry failed for ({X}, {Y}) -> {Z}"
