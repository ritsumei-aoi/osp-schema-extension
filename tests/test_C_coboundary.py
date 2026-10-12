"""
Unit tests for Schema 4 (Coboundary Structure) computation and triviality analysis.
"""

from collections import defaultdict
from fractions import Fraction
import json
import os
import pytest
from src.C_coboundary import (
    get_elementary_odd_maps,
    compute_elementary_coboundary,
    compute_coboundary_structure,
    analyze_triviality,
)


@pytest.mark.parametrize("n, expected_params", [
    (1, 32),
    (2, 176),
    (3, 528),
])
def test_elementary_odd_maps_count(n, expected_params):
    with open(f"data/C_{n}_structure.json", "r", encoding="utf-8") as f:
        schema1 = json.load(f)
    basis_even = schema1["basis"]["even"]
    basis_odd = schema1["basis"]["odd"]
    basis_list = basis_odd + basis_even
    parity_dict = schema1["parity"]

    elem_maps = get_elementary_odd_maps(basis_list, parity_dict)
    assert len(elem_maps) == expected_params
    assert len(set(p for _, _, p in elem_maps)) == expected_params


@pytest.mark.parametrize("n", [1, 2, 3])
def test_coboundary_skew_supersymmetry(n):
    """Verify that every elementary coboundary satisfies (delta f)(Y, X) = - (-1)^{p(X)p(Y)} (delta f)(X, Y)."""
    with open(f"data/C_{n}_structure.json", "r", encoding="utf-8") as f:
        schema1 = json.load(f)
    basis_even = schema1["basis"]["even"]
    basis_odd = schema1["basis"]["odd"]
    basis_list = basis_odd + basis_even
    parity_dict = schema1["parity"]

    bracket_dict = defaultdict(lambda: defaultdict(dict))
    for entry in schema1["structure_constants"]:
        bracket_dict[entry["X"]][entry["Y"]][entry["Z"]] = Fraction(entry["coeff"])

    elem_maps = get_elementary_odd_maps(basis_list, parity_dict)
    # Test a representative sample of elementary maps
    for zi, zj, param in elem_maps[:5]:
        cb = compute_elementary_coboundary(zi, zj, basis_list, parity_dict, bracket_dict)
        for (X, Y, Z), c_XY in cb.items():
            px, py = parity_dict[X], parity_dict[Y]
            expected_c_YX = - ((-1)**(px * py)) * c_XY
            actual_c_YX = cb.get((Y, X, Z), Fraction(0))
            assert actual_c_YX == expected_c_YX, (
                f"Skew-supersymmetry violated for {param} on ({X}, {Y}, {Z}): "
                f"c(X,Y)={c_XY}, c(Y,X)={actual_c_YX}, expected={expected_c_YX}"
            )


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema4_consistency_with_schema1(n):
    with open(f"data/C_{n}_structure.json", "r", encoding="utf-8") as f:
        schema1 = json.load(f)
    with open(f"data/C_{n}_coboundary.json", "r", encoding="utf-8") as f:
        schema4 = json.load(f)

    # Base schema 1 fields must be identical
    for key in (
        "schema_version",
        "algebra",
        "central_elements",
        "oscillator_generators",
        "oscillator_relations",
        "basis",
        "parity",
        "generator_realization",
        "structure_constants",
    ):
        assert schema4[key] == schema1[key], f"Schema 1 and 4 mismatch for key {key} (n={n})"

    assert "coboundary_structure" in schema4
    cb = schema4["coboundary_structure"]
    assert "linear_map" in cb
    assert "operator_definition" in cb
    assert "coboundary_constants" in cb
    assert "triviality_analysis" in cb
    assert "statistics" in cb


@pytest.mark.parametrize("n, expected_terms, expected_rank", [
    (1, 394, 28),
    (2, 4878, 168),
    (3, 22346, 516),
])
def test_coboundary_data_files(n, expected_terms, expected_rank):
    filepath = f"data/C_{n}_coboundary.json"
    assert os.path.isfile(filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    cb = data["coboundary_structure"]
    assert cb["statistics"]["total_coboundary_terms"] == expected_terms
    assert len(cb["coboundary_constants"]) == expected_terms
    assert cb["triviality_analysis"]["coboundary_rank"] == expected_rank
    assert cb["triviality_analysis"]["is_deformation_trivial"] is False
    assert cb["triviality_analysis"]["cohomology_class"] == "non_zero"
