"""
Unit tests for Schema 2 (gamma structure) for C(n+1).
"""

import json
import os
import pytest
from fractions import Fraction
from src.C_gamma import generate_schema2_data, get_gb_params


@pytest.mark.parametrize("n,expected_param_count", [
    (1, 4),
    (2, 8),
    (3, 12),
])
def test_gb_parameters_and_matrix(n, expected_param_count):
    params = get_gb_params(n)
    assert len(params) == expected_param_count

    data = generate_schema2_data(n)
    assert data["gb_parameters"] == params
    assert data["gb_matrix"]["shape"] == [2, 2 * n]
    assert len(data["gb_matrix"]["rows"]) == 2
    assert len(data["gb_matrix"]["cols"]) == 2 * n


@pytest.mark.parametrize("n", [1, 2, 3])
def test_gamma_parity_and_antisymmetry(n):
    filepath = f"data/C_{n}_gamma.json"
    assert os.path.exists(filepath)

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    parity = data["parity"]
    gamma_entries = data["inhomogeneous_deformation"]["gamma_structure"]

    # Build lookup: (X, Y, param) -> Dict[Z, Fraction]
    lookup = {}
    for entry in gamma_entries:
        x = entry["X"]
        y = entry["Y"]
        z = entry["Z"]
        param = entry["param"]
        c = Fraction(entry["coeff"])

        key = (x, y, param)
        if key not in lookup:
            lookup[key] = {}
        lookup[key][z] = c

        # Check parity condition: p(Z) == p(X) + p(Y) + 1 (mod 2)
        px = parity[x]
        py = parity[y]
        pz = parity[z]
        assert pz == (px + py + 1) % 2, (
            f"Parity violation in gamma for [{x}, {y}] -> {z}: "
            f"p(X)={px}, p(Y)={py}, p(Z)={pz}"
        )

    # Check super-antisymmetry: gamma(Y, X, p) = - (-1)^{p(X)p(Y)} gamma(X, Y, p)
    for (x, y, param), z_dict in lookup.items():
        px, py = parity[x], parity[y]
        sign = -1 if (px == 1 and py == 1) else 1
        expected_factor = -sign

        opposite_dict = lookup.get((y, x, param), {})
        for z, c in z_dict.items():
            assert z in opposite_dict, f"Missing opposite bracket ({y}, {x}, {param}) for {z}"
            assert opposite_dict[z] == expected_factor * c, (
                f"Antisymmetry violation for [{x}, {y}] vs [{y}, {x}] on {z} with {param}"
            )
