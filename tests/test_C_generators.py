"""
test_C_generators.py: Unit tests for C(n+1) basis, generator counts, parity,
and Schema 1 structure constants for n=1, 2, 3.
"""

import json
import os
import pytest
from src.C_generators import (
    build_basis,
    build_oscillator_realizations,
    compute_structure_constants,
    generate_schema1,
)


@pytest.mark.parametrize("n, expected_even, expected_odd, expected_total", [
    (1, 4, 4, 8),
    (2, 11, 8, 19),
    (3, 22, 12, 34),
])
def test_generator_counts(n, expected_even, expected_odd, expected_total):
    basis = build_basis(n)
    assert len(basis["even"]) == expected_even
    assert len(basis["odd"]) == expected_odd
    assert len(basis["even"]) + len(basis["odd"]) == expected_total

    # Verify theoretical formulas
    assert expected_even == 2 * n**2 + n + 1
    assert expected_odd == 4 * n
    assert expected_total == 2 * n**2 + 5 * n + 1


@pytest.mark.parametrize("n", [1, 2, 3])
def test_parity_consistency(n):
    gens, parities, realizations = build_oscillator_realizations(n)
    basis = build_basis(n)

    for gen in basis["even"]:
        assert parities[gen] == 0, f"Generator {gen} in basis.even must have parity 0"
        assert realizations["realizations"][gen]["parity"] == 0

    for gen in basis["odd"]:
        assert parities[gen] == 1, f"Generator {gen} in basis.odd must have parity 1"
        assert realizations["realizations"][gen]["parity"] == 1


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema_keys_and_rules(n):
    schema = generate_schema1(n)
    
    # Required top-level keys
    required_top_keys = {
        "schema_version", "algebra", "oscillator_generators",
        "central_elements", "oscillator_relations", "basis",
        "parity", "generator_realization", "structure_constants", "metadata"
    }
    assert required_top_keys.issubset(schema.keys())

    # Mandatory unified rules
    assert schema["algebra"]["family"] == "C"
    assert schema["algebra"]["m"] == 1
    assert schema["algebra"]["n"] == n
    assert schema["algebra"]["cartan_type"] == f"C({n+1})"
    assert schema["algebra"]["dimension"]["even"] == 2 * n**2 + n + 1
    assert schema["algebra"]["dimension"]["odd"] == 4 * n
    assert schema["algebra"]["dimension"]["total"] == 2 * n**2 + 5 * n + 1

    # Central elements
    assert "kappa" in schema["central_elements"]
    assert schema["central_elements"]["kappa"]["parity"] == 1
    assert "K" in schema["central_elements"]
    assert schema["central_elements"]["K"]["parity"] == 0

    # Oscillator generators
    assert "fermions" in schema["oscillator_generators"]
    assert schema["oscillator_generators"]["fermions"]["m"] == 1
    assert schema["oscillator_generators"]["fermions"]["labels"] == ["a_1_p", "a_1_m"]
    assert "bosons" in schema["oscillator_generators"]
    assert schema["oscillator_generators"]["bosons"]["n"] == n
    assert len(schema["oscillator_generators"]["bosons"]["labels"]) == 2 * n


@pytest.mark.parametrize("n", [1, 2, 3])
def test_structure_constants_parity_grading(n):
    schema = generate_schema1(n)
    parities = schema["parity"]

    for entry in schema["structure_constants"]:
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        p_x = parities[x]
        p_y = parities[y]
        p_z = parities[z]
        # Super Lie bracket preserves parity: p([X, Y]) = (p(X) + p(Y)) mod 2 == p(Z)
        assert (p_x + p_y) % 2 == p_z, (
            f"Bracket [{x}, {y}] -> {z} violates parity grading! "
            f"p({x})={p_x}, p({y})={p_y}, p({z})={p_z}"
        )


@pytest.mark.parametrize("n", [1, 2, 3])
def test_saved_json_files_exist_and_valid(n):
    filepath = os.path.join("data", f"C_{n}_structure.json")
    assert os.path.exists(filepath), f"File {filepath} should exist"
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["schema_version"] == "5.0"
    assert data["algebra"]["cartan_type"] == f"C({n+1})"
