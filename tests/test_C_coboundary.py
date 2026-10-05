"""
Unit tests for Layer 4 (coboundary structure) for C(n+1).
"""

import json
import os
import pytest
from fractions import Fraction


@pytest.mark.parametrize("n,expected_f_dim", [
    (1, 32),   # 2 * 4 * 4 = 32
    (2, 176),  # 2 * 11 * 8 = 176
    (3, 528),  # 2 * 22 * 12 = 528
])
def test_f_map_dimensions(n, expected_f_dim):
    filepath = f"data/C_{n}_coboundary.json"
    assert os.path.exists(filepath)

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    f_params = data["f_map_parameters"]["parameters"]
    assert len(f_params) == expected_f_dim
    assert data["coboundary_operator"]["f_dim"] == expected_f_dim


@pytest.mark.parametrize("n", [1, 2, 3])
def test_coboundary_parity_and_antisymmetry(n):
    filepath = f"data/C_{n}_coboundary.json"
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    parity = data["parity"]
    entries = data["coboundary_operator"]["coboundary_structure"]

    # Build lookup: (X, Y, f_param) -> Dict[Z, Fraction]
    lookup = {}
    for entry in entries:
        x = entry["X"]
        y = entry["Y"]
        z = entry["Z"]
        f_param = entry["f_param"]
        c = Fraction(entry["coeff"])

        key = (x, y, f_param)
        if key not in lookup:
            lookup[key] = {}
        lookup[key][z] = c

        px, py, pz = parity[x], parity[y], parity[z]
        assert pz == (px + py + 1) % 2, (
            f"Coboundary parity failure on ({x}, {y}, {f_param}) -> {z}"
        )

    # Super-antisymmetry
    for (x, y, f_param), z_dict in lookup.items():
        px, py = parity[x], parity[y]
        sign = -1 if (px == 1 and py == 1) else 1
        expected_factor = -sign

        opposite_dict = lookup.get((y, x, f_param), {})
        for z, c in z_dict.items():
            assert z in opposite_dict, f"Missing opposite coboundary entry ({y}, {x}, {f_param}) for {z}"
            assert opposite_dict[z] == expected_factor * c
