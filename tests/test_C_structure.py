"""
Unit tests for C(n+1) structure constants generator and JSON schema.
"""

from fractions import Fraction
import json
import os
import pytest
from src.C_generators import build_basis, build_c_structure_schema, save_c_structure


@pytest.mark.parametrize("n,expected_even,expected_odd,expected_total", [
    (1, 4, 4, 8),
    (2, 11, 8, 19),
    (3, 22, 12, 34),
])
def test_generator_counts_and_parity(n, expected_even, expected_odd, expected_total):
    even_basis, odd_basis = build_basis(n)
    assert len(even_basis) == expected_even
    assert len(odd_basis) == expected_odd
    assert len(even_basis) + len(odd_basis) == expected_total

    for g in even_basis:
        assert g["parity"] == 0
    for g in odd_basis:
        assert g["parity"] == 1


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema_structure_and_keys(n):
    schema = build_c_structure_schema(n)
    required_keys = [
        "schema_version", "algebra", "central_elements",
        "oscillator_generators", "oscillator_relations",
        "basis", "parity", "generator_realization",
        "structure_constants", "metadata"
    ]
    for key in required_keys:
        assert key in schema

    assert schema["schema_version"] == "5.0"
    assert schema["algebra"]["family"] == "C"
    assert schema["algebra"]["m"] == 1
    assert schema["algebra"]["n"] == n
    assert schema["algebra"]["dimension"]["even"] == 2 * n**2 + n + 1
    assert schema["algebra"]["dimension"]["odd"] == 4 * n
    assert schema["algebra"]["dimension"]["total"] == 2 * n**2 + 5 * n + 1


@pytest.mark.parametrize("n", [1, 2, 3])
def test_bracket_graded_antisymmetry(n):
    schema = build_c_structure_schema(n)
    parity = schema["parity"]
    brackets = {}
    for item in schema["structure_constants"]:
        x, y, z = item["X"], item["Y"], item["Z"]
        c = Fraction(item["coeff"])
        brackets[(x, y, z)] = c

    # Check for all pairs X, Y that [Y, X, Z] = - (-1)^{p(X)p(Y)} [X, Y, Z]
    all_generators = schema["basis"]["odd"] + schema["basis"]["even"]
    for x in all_generators:
        for y in all_generators:
            sign = -1 if (parity[x] == 1 and parity[y] == 1) else 1
            for z in all_generators:
                c_xy = brackets.get((x, y, z), Fraction(0))
                c_yx = brackets.get((y, x, z), Fraction(0))
                # c_yx must equal -sign * c_xy
                assert c_yx == -sign * c_xy, f"Graded antisymmetry failed for ({x}, {y}) -> {z}"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_json_files_exist_and_valid(n, tmp_path):
    filepath = os.path.join("data", f"C_{n}_structure.json")
    assert os.path.exists(filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["algebra"]["cartan_type"] == f"C({n+1})"
