"""
Unit tests for Schema 4 (Coboundary Structure) Generator
"""

import pytest
import os
import json
from src.C_coboundary_generators import compute_coboundary_matrix

def test_coboundary_phi_counts():
    for n in [1, 2, 3]:
        data = compute_coboundary_matrix(n)
        assert data["schema_version"] == "5.0"
        dim_even = 2 * n**2 + n + 1
        dim_odd = 4 * n
        # f is odd linear map: f(even)->odd (dim_even * dim_odd) + f(odd)->even (dim_odd * dim_even)
        expected_phi_count = 2 * dim_even * dim_odd
        assert data["odd_linear_map_f"]["total_phi_parameters"] == expected_phi_count

def test_coboundary_json_files():
    for n in [1, 2, 3]:
        filepath = os.path.join("data", f"C_{n}_coboundary.json")
        assert os.path.isfile(filepath)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["algebra"]["family"] == "C"
        assert len(data["coboundary_structure"]["coefficients"]) > 0
