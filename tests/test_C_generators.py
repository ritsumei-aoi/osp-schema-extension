"""
Unit tests for C(n+1) structure constant generators and Schema 1 validation.
"""

import os
import json
import pytest
from src.C_generators import (
    build_c_basis,
    compute_structure_constants,
    generate_all_schemas,
)


@pytest.mark.parametrize("n, expected_even, expected_odd, expected_total", [
    (1, 4, 4, 8),
    (2, 11, 8, 19),
    (3, 22, 12, 34),
])
def test_basis_dimensions(n, expected_even, expected_odd, expected_total):
    even_basis, odd_basis, generators = build_c_basis(n)
    assert len(even_basis) == expected_even
    assert len(odd_basis) == expected_odd
    assert len(even_basis) + len(odd_basis) == expected_total
    assert len(generators) == expected_total


@pytest.mark.parametrize("n", [1, 2, 3])
def test_parity_consistency(n):
    even_basis, odd_basis, generators = build_c_basis(n)
    for g in even_basis:
        assert generators[g]["parity"] == 0
    for g in odd_basis:
        assert generators[g]["parity"] == 1


@pytest.mark.parametrize("n", [1, 2, 3])
def test_structure_constants_and_jacobi(n):
    constants, schema_data = compute_structure_constants(n)
    assert len(constants) > 0
    assert schema_data["algebra"]["family"] == "C"
    assert schema_data["algebra"]["m"] == 1
    assert schema_data["algebra"]["n"] == n

    # Check that brackets preserve parity: p(Z) = (p(X) + p(Y)) mod 2
    parity = schema_data["parity"]
    for sc in constants:
        pX = parity[sc["X"]]
        pY = parity[sc["Y"]]
        pZ = parity[sc["Z"]]
        assert pZ == (pX + pY) % 2, f"Parity violated in [{sc['X']}, {sc['Y']}] -> {sc['Z']}"

    # Verify skew-supersymmetry: [Y, X} = -(-1)^{pX pY} [X, Y}
    bracket_dict = {}
    for sc in constants:
        bracket_dict[(sc["X"], sc["Y"], sc["Z"])] = float(sc["coeff"])

    all_basis = schema_data["basis"]["even"] + schema_data["basis"]["odd"]
    for sc in constants:
        X, Y, Z = sc["X"], sc["Y"], sc["Z"]
        pX, pY = parity[X], parity[Y]
        sign = -1 if (pX * pY) % 2 == 1 else 1
        c_xy = bracket_dict.get((X, Y, Z), 0.0)
        c_yx = bracket_dict.get((Y, X, Z), 0.0)
        assert abs(c_yx - (-sign * c_xy)) < 1e-9


def test_schema_keys():
    _, schema_data = compute_structure_constants(1)
    required_keys = [
        "schema_version",
        "algebra",
        "central_elements",
        "oscillator_generators",
        "oscillator_relations",
        "basis",
        "parity",
        "generator_realization",
        "structure_constants",
        "metadata",
    ]
    for key in required_keys:
        assert key in schema_data
    assert "kappa" in schema_data["central_elements"]
    assert "K" in schema_data["central_elements"]
    assert "fermions" in schema_data["oscillator_generators"]
    assert "bosons" in schema_data["oscillator_generators"]


def test_generated_json_files(tmp_path):
    out_dir = str(tmp_path)
    generate_all_schemas(output_dir=out_dir)
    for n in (1, 2, 3):
        filepath = os.path.join(out_dir, f"C_{n}_structure.json")
        assert os.path.isfile(filepath)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert data["algebra"]["cartan_type"] == f"C({n+1})"
            assert data["schema_version"] == "5.0"
