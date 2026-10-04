"""
Unit tests for C(n+1) generator and Schema 1 JSON structures.
"""

import json
import pytest
from fractions import Fraction
from src.C_generators import CSuperalgebra, generate_all_schema1


@pytest.mark.parametrize("n, expected_even, expected_odd, expected_total", [
    (1, 4, 4, 8),
    (2, 11, 8, 19),
    (3, 22, 12, 34),
])
def test_generator_counts_and_dimensions(n, expected_even, expected_odd, expected_total):
    alg = CSuperalgebra(n)
    assert len(alg.basis_even) == expected_even
    assert len(alg.basis_odd) == expected_odd
    assert len(alg.basis_all) == expected_total
    assert alg.even_dim == expected_even
    assert alg.odd_dim == expected_odd
    assert alg.total_dim == expected_total


@pytest.mark.parametrize("n", [1, 2, 3])
def test_parity_consistency(n):
    alg = CSuperalgebra(n)
    for x in alg.basis_even:
        assert alg.parity[x] == 0
    for x in alg.basis_odd:
        assert alg.parity[x] == 1


@pytest.mark.parametrize("n", [1, 2, 3])
def test_graded_skew_symmetry(n):
    alg = CSuperalgebra(n)
    sc = alg.compute_structure_constants()
    
    # Store brackets as (X, Y) -> {Z: coeff}
    brackets = {}
    for entry in sc:
        X, Y, Z, coeff = entry["X"], entry["Y"], entry["Z"], Fraction(entry["coeff"])
        brackets.setdefault((X, Y), {})[Z] = coeff

    # Check [Y, X} = -(-1)^(p(X)p(Y)) [X, Y}
    for (X, Y), z_dict in brackets.items():
        pX, pY = alg.parity[X], alg.parity[Y]
        expected_sign = -1 if (pX * pY == 0) else 1  # -(-1)^(pX*pY)

        yx_dict = brackets.get((Y, X), {})
        for Z, c in z_dict.items():
            assert Z in yx_dict, f"Missing opposite pair for ({Y}, {X}) -> {Z}"
            assert yx_dict[Z] == expected_sign * c, f"Skew-symmetry failed for ({X}, {Y}) -> {Z}"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema_json_generation(n):
    generate_all_schema1()
    with open(f"data/C_{n}_structure.json", "r") as f:
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
    assert len(data["basis"]["even"]) == 2 * n * n + n + 1
    assert len(data["basis"]["odd"]) == 4 * n
