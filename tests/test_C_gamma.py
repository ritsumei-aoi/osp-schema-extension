import os
import json
import pytest
from fractions import Fraction
from src.C_gamma import generate_C_gamma_json, save_all_C_gamma_json

def test_gamma_gb_parameters():
    for n in (1, 2, 3):
        data = generate_C_gamma_json(n)
        gb_info = data["gb_parameters"]
        assert gb_info["count"] == 4 * n
        assert gb_info["matrix_shape"] == [2, 2 * n]
        assert len(gb_info["labels"]) == 4 * n
        assert len(gb_info["row_labels"]) == 2
        assert len(gb_info["column_labels"]) == 2 * n

def test_gamma_file_generation():
    save_all_C_gamma_json()
    for n in (1, 2, 3):
        filepath = f"data/C_{n}_gamma.json"
        assert os.path.exists(filepath)
        with open(filepath, "r") as f:
            data = json.load(f)

        assert data["schema_version"] == "5.0"
        assert data["algebra"]["family"] == "C"
        assert data["algebra"]["m"] == 1
        assert data["algebra"]["n"] == n
        assert "gamma_terms" in data
        assert len(data["gamma_terms"]) > 0

def test_gamma_graded_antisymmetry_and_parity():
    for n in (1, 2, 3):
        filepath_struct = f"data/C_{n}_structure.json"
        with open(filepath_struct, "r") as f:
            data_struct = json.load(f)
        parity = data_struct["parity"]

        data_gamma = generate_C_gamma_json(n)
        gamma_map = {}
        for entry in data_gamma["gamma_terms"]:
            x, y, z, gb, coeff = entry["X"], entry["Y"], entry["Z"], entry["gb_param"], entry["coeff"]
            # Parity check: Since kappa is odd (parity 1), gamma(X, Y) has parity (p(X) + p(Y) + 1) % 2
            assert parity[z] == (parity[x] + parity[y] + 1) % 2, f"Gamma parity mismatch for ({x}, {y}, {z})"
            gamma_map[(x, y, z, gb)] = Fraction(coeff)

        basis = data_struct["basis"]["odd"] + data_struct["basis"]["even"]
        gb_labels = data_gamma["gb_parameters"]["labels"]

        for x in basis:
            for y in basis:
                px, py = parity[x], parity[y]
                sign = -1 if (px == 1 and py == 1) else 1
                for z in basis:
                    for gb in gb_labels:
                        c1 = gamma_map.get((x, y, z, gb), Fraction(0))
                        c2 = gamma_map.get((y, x, z, gb), Fraction(0))
                        assert c1 == -sign * c2, f"Gamma graded antisymmetry violation for ({x}, {y}) on {z} ({gb})"
