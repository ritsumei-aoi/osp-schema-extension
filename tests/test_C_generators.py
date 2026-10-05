"""Tests for C(n+1) structure constant generator."""
import json
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from C_generators import build_basis, build_parity, generate_schema1


@pytest.mark.parametrize("n,expected_even,expected_odd", [
    (1, 4, 4),
    (2, 11, 8),
    (3, 22, 12),
])
def test_basis_counts(n, expected_even, expected_odd):
    even, odd = build_basis(n)
    assert len(even) == expected_even, f"n={n}: even count {len(even)} != {expected_even}"
    assert len(odd) == expected_odd, f"n={n}: odd count {len(odd)} != {expected_odd}"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_parity_assignment(n):
    even, odd = build_basis(n)
    parity = build_parity(even, odd)
    for g in even:
        assert parity[g] == 0, f"{g} should be even"
    for g in odd:
        assert parity[g] == 1, f"{g} should be odd"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_dimension_formula(n):
    schema = generate_schema1(n)
    dim = schema["algebra"]["dimension"]
    assert dim["even"] == 2 * n * n + n + 1
    assert dim["odd"] == 4 * n
    assert dim["total"] == dim["even"] + dim["odd"]


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema_structure(n):
    schema = generate_schema1(n)
    assert schema["schema_version"] == "5.0"
    assert schema["algebra"]["family"] == "C"
    assert schema["algebra"]["m"] == 1
    assert schema["algebra"]["n"] == n
    assert "fermions" in schema["oscillator_generators"]
    assert "bosons" in schema["oscillator_generators"]
    assert "kappa" in schema["central_elements"]
    assert "K" in schema["central_elements"]
    assert schema["central_elements"]["kappa"]["parity"] == 1
    assert schema["central_elements"]["K"]["parity"] == 0


@pytest.mark.parametrize("n", [1, 2, 3])
def test_generator_labels_unique(n):
    even, odd = build_basis(n)
    all_gens = even + odd
    assert len(all_gens) == len(set(all_gens)), "Duplicate generator labels"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_json_output(n):
    filename = f"data/C_{n}_structure.json"
    with open(filename) as f:
        data = json.load(f)
    assert data["schema_version"] == "5.0"
    assert len(data["structure_constants"]) > 0
    for sc in data["structure_constants"]:
        assert "X" in sc
        assert "Y" in sc
        assert "Z" in sc
        assert "coeff" in sc


@pytest.mark.parametrize("n", [1, 2, 3])
def test_structure_constants_parity(n):
    schema = generate_schema1(n)
    parity = schema["parity"]
    for sc in schema["structure_constants"]:
        X, Y, Z = sc["X"], sc["Y"], sc["Z"]
        if Z == "scalar":
            continue
        pX, pY, pZ = parity[X], parity[Y], parity[Z]
        expected_parity = (pX + pY) % 2
        assert pZ == expected_parity, (
            f"Parity violation: [{X}(p={pX}), {Y}(p={pY})] -> {Z}(p={pZ}), expected p={expected_parity}"
        )
