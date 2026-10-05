"""
Unit tests for Schema 2 gamma structure generator.
"""

import os
import json
import pytest
from src.C_gamma_generators import build_C_gamma_structure

@pytest.mark.parametrize("n, expected_gb_count", [
    (1, 4),
    (2, 8),
    (3, 12),
])
def test_gb_matrix_size(n, expected_gb_count):
    data = build_C_gamma_structure(n)
    gb_info = data["gb_matrix"]
    assert gb_info["count"] == expected_gb_count
    assert len(gb_info["parameters"]) == expected_gb_count


def test_schema_2_consistency_with_schema_1():
    for n in [1, 2, 3]:
        with open(f"data/C_{n}_structure.json") as f:
            struct_data = json.load(f)
        with open(f"data/C_{n}_gamma.json") as f:
            gamma_data = json.load(f)

        all_basis = set(struct_data["basis"]["odd"]).union(set(struct_data["basis"]["even"]))
        parity_map = struct_data["parity"]

        for entry in gamma_data["gamma_structure"]:
            x, y = entry["X"], entry["Y"]
            assert x in all_basis
            assert y in all_basis
            px, py = parity_map[x], parity_map[y]
            expected_pz = (px + py + 1) % 2

            for gb_param, term_list in entry["gamma_value"].items():
                for term in term_list:
                    z = term["Z"]
                    assert z in all_basis, f"Target {z} not in basis"
                    pz = parity_map[z]
                    assert pz == expected_pz, f"Parity mismatch for gamma({x},{y}) -> {z}: got {pz}, expected {expected_pz}"
