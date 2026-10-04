"""
Unit tests for Schema 3 (Evaluated Structure) Generator
"""

import pytest
import os
import json
from src.C_evaluated_generators import evaluate_gamma_structure

def test_evaluated_assignments():
    for n in [1, 2, 3]:
        data = evaluate_gamma_structure(n)
        assert data["schema_version"] == "5.0"
        assert len(data["gb_assignment"]) == 4 * n
        for val in data["gb_assignment"].values():
            assert val == "1"

def test_evaluated_consistency_with_gamma():
    for n in [1, 2, 3]:
        eval_data = evaluate_gamma_structure(n)
        eval_terms = eval_data["evaluated_deformation"]["coefficients"]
        assert len(eval_terms) > 0
        
        # Check all X, Y, Z elements exist in basis
        even = eval_data["basis"]["even"]
        odd = eval_data["basis"]["odd"]
        all_basis = set(even + odd)
        
        for entry in eval_terms:
            assert entry["X"] in all_basis
            assert entry["Y"] in all_basis
            assert entry["Z"] in all_basis

def test_evaluated_json_files():
    for n in [1, 2, 3]:
        filepath = os.path.join("data", f"C_{n}_evaluated.json")
        assert os.path.isfile(filepath)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["algebra"]["family"] == "C"
        assert len(data["evaluated_deformation"]["coefficients"]) > 0
