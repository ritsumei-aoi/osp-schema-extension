"""
Unit tests for C_generators.py
Tests basis construction, parity, dimensions, algebra closure,
skew-symmetry, and Jacobi identities for C(2), C(3), C(4).
"""

import pytest
from fractions import Fraction
from src.C_generators import (
    build_c_generators,
    compute_structure_constants,
    generate_schema_1_dict,
    graded_bracket,
    decompose_in_basis,
    Poly
)


@pytest.mark.parametrize("n, expected_even, expected_odd, expected_total", [
    (1, 4, 4, 8),
    (2, 11, 8, 19),
    (3, 22, 12, 34)
])
def test_generator_counts_and_dimensions(n, expected_even, expected_odd, expected_total):
    data = build_c_generators(n)
    even_basis = data["even_basis"]
    odd_basis = data["odd_basis"]
    
    assert len(even_basis) == expected_even
    assert len(odd_basis) == expected_odd
    assert len(even_basis) + len(odd_basis) == expected_total


@pytest.mark.parametrize("n", [1, 2, 3])
def test_parity_consistency(n):
    data = build_c_generators(n)
    even_basis = data["even_basis"]
    odd_basis = data["odd_basis"]
    parities = data["parities"]

    for name in even_basis:
        assert parities[name] == 0, f"{name} should have parity 0"

    for name in odd_basis:
        assert parities[name] == 1, f"{name} should have parity 1"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_structure_constants_graded_skew_symmetry_and_parity(n):
    data = build_c_generators(n)
    full_basis = data["odd_basis"] + data["even_basis"]
    parities = data["parities"]
    struct_consts = compute_structure_constants(n, data)

    # Convert struct_consts to dict: (X, Y, Z) -> Fraction
    table = {}
    for entry in struct_consts:
        X, Y, Z = entry["X"], entry["Y"], entry["Z"]
        coeff = Fraction(entry["coeff"])
        table[(X, Y, Z)] = coeff

        # Test parity preservation: p(Z) == (p(X) + p(Y)) % 2
        pX = parities[X]
        pY = parities[Y]
        pZ = parities[Z]
        assert pZ == (pX + pY) % 2, f"Parity violated: [{X}, {Y}] -> {Z}"

    # Test graded skew-symmetry: [Y, X, Z] == -(-1)^{pX pY} [X, Y, Z]
    for X in full_basis:
        for Y in full_basis:
            for Z in full_basis:
                c_xyz = table.get((X, Y, Z), Fraction(0))
                c_yxz = table.get((Y, X, Z), Fraction(0))
                pX, pY = parities[X], parities[Y]
                sign = -1 if (pX * pY) % 2 == 1 else 1
                expected_yxz = -c_xyz * sign
                assert c_yxz == expected_yxz, f"Skew-symmetry failed for [{X}, {Y}] vs [{Y}, {X}] on {Z}"


def test_graded_jacobi_identity_c2():
    # Full Jacobi test for C(2) (8 generators, 8^3 = 512 triples)
    data = build_c_generators(1)
    full_basis = data["odd_basis"] + data["even_basis"]
    generators = data["generators"]
    parities = data["parities"]

    bracket_cache = {}
    for X in full_basis:
        for Y in full_basis:
            bracket_cache[(X, Y)] = graded_bracket(generators[X], parities[X], generators[Y], parities[Y])

    for X in full_basis:
        for Y in full_basis:
            for Z in full_basis:
                pX, pY, pZ = parities[X], parities[Y], parities[Z]
                br_YZ = bracket_cache[(Y, Z)]
                term1 = graded_bracket(generators[X], pX, br_YZ, (pY + pZ) % 2) * ((-1)**((pX * pZ) % 2))

                br_ZX = bracket_cache[(Z, X)]
                term2 = graded_bracket(generators[Y], pY, br_ZX, (pZ + pX) % 2) * ((-1)**((pY * pX) % 2))

                br_XY = bracket_cache[(X, Y)]
                term3 = graded_bracket(generators[Z], pZ, br_XY, (pX + pY) % 2) * ((-1)**((pZ * pY) % 2))

                jac = term1 + term2 + term3
                assert len(jac.terms) == 0, f"Jacobi failed for ({X}, {Y}, {Z})"


def test_schema_1_structure_conformance():
    schema = generate_schema_1_dict(1)
    required_keys = [
        "schema_version", "algebra", "central_elements", "oscillator_generators",
        "oscillator_relations", "basis", "parity", "generator_realization",
        "structure_constants", "metadata"
    ]
    for key in required_keys:
        assert key in schema, f"Missing key {key} in schema"

    assert schema["schema_version"] == "5.0"
    assert schema["algebra"]["family"] == "C"
    assert schema["algebra"]["m"] == 1
    assert "kappa" in schema["central_elements"]
    assert "K" in schema["central_elements"]
    assert "fermions" in schema["oscillator_generators"]
    assert "bosons" in schema["oscillator_generators"]
