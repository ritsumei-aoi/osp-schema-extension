"""
Unit tests for Schema 2 (Gamma Structure) Generator
"""

import pytest
import os
import json
from src.C_gamma_generators import get_gamma_structure

def test_gb_matrix():
    for n in [1, 2, 3]:
        g = get_gamma_structure(n)
        assert g["schema_version"] == "5.0"
        assert g["gb_matrix"]["total_parameters"] == 4 * n
        assert len(g["gb_matrix"]["rows"]) == 2
        assert len(g["gb_matrix"]["cols"]) == 2 * n

def test_gamma_parity_rule():
    for n in [1, 2, 3]:
        g = get_gamma_structure(n)
        parity = g["basis"]["parity"]
        coeffs = g["inhomogeneous_deformation"]["coefficients"]
        
        for entry in coeffs:
            X, Y, Z = entry["X"], entry["Y"], entry["Z"]
            pX, pY, pZ = parity[X], parity[Y], parity[Z]
            
            # Deformed bracket [X, Y]_gamma = [X, Y]_0 + kappa * gamma(X, Y)
            # p(kappa) = 1, so parity equation: pX + pY = 1 + pZ (mod 2)
            # => pZ = (pX + pY + 1) mod 2
            expected_pZ = (pX + pY + 1) % 2
            assert pZ == expected_pZ, f"Gamma parity violation for {X}, {Y} -> {Z}: pZ={pZ} != {expected_pZ}"

def test_gamma_json_files():
    for n in [1, 2, 3]:
        filepath = os.path.join("data", f"C_{n}_gamma.json")
        assert os.path.isfile(filepath)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["algebra"]["family"] == "C"
        assert len(data["inhomogeneous_deformation"]["coefficients"]) > 0
