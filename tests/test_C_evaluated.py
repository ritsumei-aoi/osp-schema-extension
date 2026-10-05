"""
Unit tests for Layer 3 (evaluated structure) for C(n+1).
"""

import json
import os
import pytest
from fractions import Fraction
from src.C_evaluated import evaluate_gamma_structure


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema3_json_files_and_consistency(n):
    filepath = f"data/C_{n}_evaluated.json"
    assert os.path.exists(filepath)

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["schema_version"] == "5.0"
    assert "evaluated_deformation" in data
    assert "gamma_evaluated" in data["evaluated_deformation"]
    assert "gb_assignment" in data

    parity = data["parity"]
    entries = data["evaluated_deformation"]["gamma_evaluated"]

    # Check parity and antisymmetry of evaluated brackets
    lookup = {}
    for entry in entries:
        x = entry["X"]
        y = entry["Y"]
        z = entry["Z"]
        c = Fraction(entry["coeff"])

        key = (x, y)
        if key not in lookup:
            lookup[key] = {}
        lookup[key][z] = c

        px, py, pz = parity[x], parity[y], parity[z]
        assert pz == (px + py + 1) % 2

    for (x, y), z_dict in lookup.items():
        px, py = parity[x], parity[y]
        sign = -1 if (px == 1 and py == 1) else 1
        expected_factor = -sign

        opposite_dict = lookup.get((y, x), {})
        for z, c in z_dict.items():
            assert z in opposite_dict
            assert opposite_dict[z] == expected_factor * c
