"""
Unit tests for C_evaluated.py (Schema 3 / Layer 3).
"""

import os
import json
import pytest
from fractions import Fraction
from src.C_evaluated import evaluate_gamma_structure, generate_all_evaluated_files


@pytest.mark.parametrize("n", [1, 2, 3])
def test_evaluate_gamma(n):
    gamma_file = f"data/C_{n}_gamma.json"
    with open(gamma_file, "r") as f:
        gamma_data = json.load(f)

    eval_data = evaluate_gamma_structure(gamma_data)
    assert eval_data["schema_version"] == "5.0"
    assert eval_data["layer"] == "Schema 3: Evaluated Structure"
    assert len(eval_data["gb_assignment"]) == 4 * n
    assert len(eval_data["evaluated_gamma"]) > 0


def test_generate_all_evaluated_files():
    generate_all_evaluated_files("data", "data")
    for n in [1, 2, 3]:
        eval_file = os.path.join("data", f"C_{n}_evaluated.json")
        assert os.path.exists(eval_file)
        with open(eval_file, "r") as f:
            data = json.load(f)
            assert data["algebra"]["n"] == n
            assert len(data["evaluated_gamma"]) > 0
