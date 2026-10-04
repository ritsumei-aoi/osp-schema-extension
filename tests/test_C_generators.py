"""Unit tests for C(n+1) structure constant generator and Schema 1 JSON."""

import json
from fractions import Fraction
from pathlib import Path
import pytest

from src.C_generators import (
    build_c_algebra,
    compute_structure_constants,
    generate_schema1_json,
)


@pytest.mark.parametrize("n,expected_even,expected_odd,expected_total", [
    (1, 4, 4, 8),
    (2, 11, 8, 19),
    (3, 22, 12, 34),
])
def test_generator_counts_and_dimensions(n, expected_even, expected_odd, expected_total):
    even_basis, odd_basis, parities, gens, realizations = build_c_algebra(n)
    assert len(even_basis) == expected_even
    assert len(odd_basis) == expected_odd
    assert len(even_basis) + len(odd_basis) == expected_total
    assert len(parities) == expected_total
    assert len(gens) == expected_total
    assert len(realizations) == expected_total


@pytest.mark.parametrize("n", [1, 2, 3])
def test_parities(n):
    even_basis, odd_basis, parities, gens, realizations = build_c_algebra(n)
    for g in even_basis:
        assert parities[g] == 0
        assert realizations[g]["parity"] == 0
    for g in odd_basis:
        assert parities[g] == 1
        assert realizations[g]["parity"] == 1


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema1_json_conformance(n):
    path = Path(f"data/C_{n}_structure.json")
    assert path.exists()

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Top-level keys
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
    for k in required_keys:
        assert k in data, f"Missing top-level key {k}"

    assert data["schema_version"] == "5.0"
    assert data["algebra"]["family"] == "C"
    assert data["algebra"]["m"] == 1
    assert data["algebra"]["n"] == n
    assert data["algebra"]["cartan_type"] == f"C({n+1})"

    # Central elements
    assert "kappa" in data["central_elements"]
    assert data["central_elements"]["kappa"]["parity"] == 1
    assert "K" in data["central_elements"]
    assert data["central_elements"]["K"]["parity"] == 0

    # Oscillator generators
    assert data["oscillator_generators"]["fermions"]["m"] == 1
    assert data["oscillator_generators"]["fermions"]["labels"] == ["a_1_p", "a_1_m"]
    assert data["oscillator_generators"]["bosons"]["n"] == n
    assert len(data["oscillator_generators"]["bosons"]["labels"]) == 2 * n

    # Basis consistency
    all_gens = set(data["basis"]["even"] + data["basis"]["odd"])
    assert len(all_gens) == data["algebra"]["dimension"]["total"]
    assert set(data["parity"].keys()) == all_gens
    assert set(data["generator_realization"]["realizations"].keys()) == all_gens

    # Check structure constants references
    for sc in data["structure_constants"]:
        assert sc["X"] in all_gens
        assert sc["Y"] in all_gens
        assert sc["Z"] in all_gens
        assert sc["sign_rule"] == "graded"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_antisymmetry_of_structure_constants(n):
    with open(f"data/C_{n}_structure.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    parities = data["parity"]
    brackets = {}
    for sc in data["structure_constants"]:
        brackets[(sc["X"], sc["Y"], sc["Z"])] = Fraction(sc["coeff"])

    all_pairs = set((sc["X"], sc["Y"]) for sc in data["structure_constants"])
    all_gens = data["basis"]["odd"] + data["basis"]["even"]

    for x in all_gens:
        for y in all_gens:
            px, py = parities[x], parities[y]
            sign = -1 if (px * py == 1) else 1
            for z in all_gens:
                c_xy_z = brackets.get((x, y, z), Fraction(0))
                c_yx_z = brackets.get((y, x, z), Fraction(0))
                # Anti-symmetry: [Y, X} = -(-1)^(px py) [X, Y}
                assert c_yx_z == -sign * c_xy_z, f"Anti-symmetry failure for [{x}, {y}] -> {z}"
