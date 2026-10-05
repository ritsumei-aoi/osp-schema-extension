"""Tests for C(n+1) structure constant generator."""

import json
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from C_generators import (
    build_basis, build_parity_map, gen_realization,
    compute_all_structure_constants, build_schema1_json,
)


@pytest.mark.parametrize("n,expected_even,expected_odd", [
    (1, 4, 4),
    (2, 11, 8),
    (3, 22, 12),
])
def test_basis_counts(n, expected_even, expected_odd):
    even, odd = build_basis(n)
    assert len(even) == expected_even, f"n={n}: even={len(even)}, expected={expected_even}"
    assert len(odd) == expected_odd, f"n={n}: odd={len(odd)}, expected={expected_odd}"


@pytest.mark.parametrize("n,expected_even,expected_odd", [
    (1, 4, 4),
    (2, 11, 8),
    (3, 22, 12),
])
def test_dimension_formula(n, expected_even, expected_odd):
    assert 2 * n * n + n + 1 == expected_even
    assert 4 * n == expected_odd


@pytest.mark.parametrize("n", [1, 2, 3])
def test_parity_consistency(n):
    even, odd = build_basis(n)
    parity = build_parity_map(even, odd)
    for g in even:
        assert parity[g] == 0, f"{g} should be even"
    for g in odd:
        assert parity[g] == 1, f"{g} should be odd"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_all_generators_have_realization(n):
    even, odd = build_basis(n)
    reals = gen_realization(n)
    for g in even + odd:
        assert g in reals, f"Missing realization for {g}"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_structure_constants_parity(n):
    even, odd = build_basis(n)
    parity = build_parity_map(even, odd)
    constants = compute_all_structure_constants(n)
    for sc in constants:
        pX = parity[sc["X"]]
        pY = parity[sc["Y"]]
        pZ = parity[sc["Z"]]
        assert (pX + pY) % 2 == pZ, (
            f"Parity violation: [{sc['X']}(p={pX}), {sc['Y']}(p={pY})] -> "
            f"{sc['Z']}(p={pZ}), expected p={((pX + pY) % 2)}"
        )


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema1_json_valid(n):
    schema = build_schema1_json(n)
    assert schema["schema_version"] == "5.0"
    assert schema["algebra"]["family"] == "C"
    assert schema["algebra"]["m"] == 1
    assert schema["algebra"]["n"] == n
    assert "central_elements" in schema
    assert "kappa" in schema["central_elements"]
    assert "K" in schema["central_elements"]
    assert schema["central_elements"]["kappa"]["parity"] == 1
    assert schema["central_elements"]["K"]["parity"] == 0


@pytest.mark.parametrize("n", [1, 2, 3])
def test_json_files_exist(n):
    path = os.path.join(os.path.dirname(__file__), '..', 'data', f'C_{n}_structure.json')
    assert os.path.exists(path), f"Missing {path}"
    with open(path) as f:
        data = json.load(f)
    assert data["schema_version"] == "5.0"
    assert len(data["basis"]["even"]) == 2 * n * n + n + 1
    assert len(data["basis"]["odd"]) == 4 * n


@pytest.mark.parametrize("n", [1, 2, 3])
def test_nonzero_structure_constants(n):
    constants = compute_all_structure_constants(n)
    assert len(constants) > 0, f"No structure constants for n={n}"
