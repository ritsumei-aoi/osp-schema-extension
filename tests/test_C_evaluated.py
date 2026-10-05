import os
import json
import pytest
from fractions import Fraction
from src.C_evaluated import generate_C_evaluated_json, save_all_C_evaluated_json

def test_evaluated_file_generation():
    save_all_C_evaluated_json()
    for n in (1, 2, 3):
        filepath = f"data/C_{n}_evaluated.json"
        assert os.path.exists(filepath)
        with open(filepath, "r") as f:
            data = json.load(f)

        assert data["schema_version"] == "5.0"
        assert data["algebra"]["family"] == "C"
        assert data["algebra"]["m"] == 1
        assert data["algebra"]["n"] == n
        assert "gb_evaluation" in data
        assert data["gb_evaluation"]["profile"] == "all_plus_one"
        assert len(data["gb_evaluation"]["values"]) == 4 * n
        assert "evaluated_structure_constants" in data
        assert len(data["evaluated_structure_constants"]) > 0

def test_evaluated_sum_consistency():
    for n in (1, 2, 3):
        data = generate_C_evaluated_json(n)
        for entry in data["evaluated_structure_constants"]:
            c_std = Fraction(entry["coeff_standard"])
            c_gam = Fraction(entry["coeff_gamma_evaluated"])
            c_tot = Fraction(entry["coeff_total"])
            assert c_tot == c_std + c_gam, f"Sum mismatch in evaluated constants for ({entry['X']}, {entry['Y']}, {entry['Z']})"
