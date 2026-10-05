import os
import json
import pytest
from fractions import Fraction
from src.C_coboundary import generate_C_coboundary_json, save_all_C_coboundary_json

def test_coboundary_parameter_counts():
    for n in (1, 2, 3):
        data = generate_C_coboundary_json(n)
        dim_even = 2 * n**2 + n + 1
        dim_odd = 4 * n
        expected_phi_count = 2 * dim_even * dim_odd
        assert data["linear_map_f"]["parameter_count"] == expected_phi_count

def test_coboundary_file_generation():
    save_all_C_coboundary_json()
    for n in (1, 2, 3):
        filepath = f"data/C_{n}_coboundary.json"
        assert os.path.exists(filepath)
        with open(filepath, "r") as f:
            data = json.load(f)

        assert data["schema_version"] == "5.0"
        assert data["algebra"]["family"] == "C"
        assert data["algebra"]["m"] == 1
        assert data["algebra"]["n"] == n
        assert "coboundary_terms" in data
        assert len(data["coboundary_terms"]) > 0

def test_coboundary_graded_antisymmetry_and_parity():
    for n in (1, 2, 3):
        filepath_struct = f"data/C_{n}_structure.json"
        with open(filepath_struct, "r") as f:
            data_struct = json.load(f)
        parity = data_struct["parity"]

        data_coboundary = generate_C_coboundary_json(n)
        cb_map = {}
        for entry in data_coboundary["coboundary_terms"]:
            x, y, z, phi, coeff = entry["X"], entry["Y"], entry["Z"], entry["phi_param"], entry["coeff"]
            assert parity[z] == (parity[x] + parity[y] + 1) % 2, f"Coboundary parity mismatch for ({x}, {y}, {z})"
            cb_map[(x, y, z, phi)] = Fraction(coeff)

        basis = data_struct["basis"]["odd"] + data_struct["basis"]["even"]
        phi_params = [p["name"] for p in data_coboundary["linear_map_f"]["parameters"]]

        for x in basis:
            for y in basis:
                px, py = parity[x], parity[y]
                sign = -1 if (px == 1 and py == 1) else 1
                for z in basis:
                    for phi in phi_params:
                        c1 = cb_map.get((x, y, z, phi), Fraction(0))
                        c2 = cb_map.get((y, x, z, phi), Fraction(0))
                        assert c1 == -sign * c2, f"Coboundary graded antisymmetry violation for ({x}, {y}) on {z} ({phi})"
