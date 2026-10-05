"""
Unit tests for Schema 4 coboundary generator.
"""

import os
import json
import pytest
from src.C_coboundary_generators import build_C_coboundary_structure

@pytest.mark.parametrize("n, expected_even_dim, expected_odd_dim, expected_param_count", [
    (1, 4, 4, 32),
    (2, 11, 8, 176),
    (3, 22, 12, 528),
])
def test_f_matrix_parameter_count(n, expected_even_dim, expected_odd_dim, expected_param_count):
    data = build_C_coboundary_structure(n)
    f_info = data["f_matrix_info"]
    assert f_info["even_dim"] == expected_even_dim
    assert f_info["odd_dim"] == expected_odd_dim
    assert f_info["parameter_count"] == expected_param_count


def test_coboundary_parity_consistency():
    for n in [1, 2, 3]:
        with open(f"data/C_{n}_structure.json") as f:
            struct_data = json.load(f)
        with open(f"data/C_{n}_coboundary.json") as f:
            coboundary_data = json.load(f)

        parity_map = struct_data["parity"]

        for entry in coboundary_data["coboundary_structure"]:
            x, y = entry["X"], entry["Y"]
            px, py = parity_map[x], parity_map[y]
            expected_pz = (px + py + 1) % 2

            for phi_param, term_list in entry["delta_f_value"].items():
                for term in term_list:
                    z = term["Z"]
                    pz = parity_map[z]
                    assert pz == expected_pz, f"Parity mismatch in coboundary({x},{y}) -> {z}: got {pz}, expected {expected_pz}"
