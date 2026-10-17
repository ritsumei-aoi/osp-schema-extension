"""
Unit tests for C_evaluated.py (Schema 3: Evaluated Structure).
Tests file existence, schema conformance, numerical consistency with Schema 2,
parity preservation, and graded anti-symmetry.
"""

import json
import os
import pytest
from fractions import Fraction
from collections import defaultdict


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema_3_disk_files_and_schema_conformance(n):
    eval_path = os.path.join("data", f"C_{n}_evaluated.json")
    gamma_path = os.path.join("data", f"C_{n}_gamma.json")
    struct_path = os.path.join("data", f"C_{n}_structure.json")

    assert os.path.exists(eval_path), f"File {eval_path} does not exist"

    with open(eval_path, "r", encoding="utf-8") as f:
        data_eval = json.load(f)

    with open(gamma_path, "r", encoding="utf-8") as f:
        data_gamma = json.load(f)

    with open(struct_path, "r", encoding="utf-8") as f:
        data_struct = json.load(f)

    # 1. Top-level keys
    required_keys = [
        "schema_version", "algebra", "central_elements", "evaluated_parameters",
        "basis", "parity", "evaluated_gamma_structure_constants",
        "total_evaluated_bracket", "metadata"
    ]
    for key in required_keys:
        assert key in data_eval, f"Missing key {key} in {eval_path}"

    assert data_eval["schema_version"] == "5.0"
    assert data_eval["algebra"] == data_struct["algebra"]
    assert data_eval["central_elements"] == data_struct["central_elements"]
    assert data_eval["basis"] == data_struct["basis"]
    assert data_eval["parity"] == data_struct["parity"]

    # 2. Evaluated parameters profile
    eval_params = data_eval["evaluated_parameters"]
    assert eval_params["profile_name"] == "all_plus_one"
    assert len(eval_params["parameter_values"]) == 4 * n
    for param_name, val in eval_params["parameter_values"].items():
        assert val == "1"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_numerical_consistency_with_schema_2(n):
    eval_path = os.path.join("data", f"C_{n}_evaluated.json")
    gamma_path = os.path.join("data", f"C_{n}_gamma.json")

    with open(eval_path, "r", encoding="utf-8") as f:
        data_eval = json.load(f)

    with open(gamma_path, "r", encoding="utf-8") as f:
        data_gamma = json.load(f)

    # Sum up gamma constants from Schema 2 at all_plus_one (each param = 1)
    expected_sum = defaultdict(Fraction)
    for entry in data_gamma["gamma_structure_constants"]:
        X = entry["X"]
        Y = entry["Y"]
        Z = entry["Z"]
        coeff = Fraction(entry["coeff"])
        expected_sum[(X, Y, Z)] += coeff

    # Load evaluated constants from Schema 3
    actual_table = {}
    for entry in data_eval["evaluated_gamma_structure_constants"]:
        X = entry["X"]
        Y = entry["Y"]
        Z = entry["Z"]
        coeff = Fraction(entry["coeff"])
        actual_table[(X, Y, Z)] = coeff

    # Filter non-zero expected sums
    expected_nonzero = {k: v for k, v in expected_sum.items() if v != 0}

    assert len(actual_table) == len(expected_nonzero)
    for key, expected_val in expected_nonzero.items():
        assert key in actual_table, f"Missing key {key} in evaluated structure"
        assert actual_table[key] == expected_val, (
            f"Value mismatch for {key}: expected {expected_val}, got {actual_table[key]}"
        )


@pytest.mark.parametrize("n", [1, 2, 3])
def test_evaluated_gamma_parity_and_anti_symmetry(n):
    eval_path = os.path.join("data", f"C_{n}_evaluated.json")
    with open(eval_path, "r", encoding="utf-8") as f:
        data_eval = json.load(f)

    parity = data_eval["parity"]
    eval_list = data_eval["evaluated_gamma_structure_constants"]

    table = {}
    for entry in eval_list:
        X = entry["X"]
        Y = entry["Y"]
        Z = entry["Z"]
        coeff = Fraction(entry["coeff"])
        table[(X, Y, Z)] = coeff

        # Parity check: p(Z) == (p(X) + p(Y) + 1) % 2
        pX = parity[X]
        pY = parity[Y]
        pZ = parity[Z]
        assert pZ == (pX + pY + 1) % 2, f"Parity mismatch in evaluated gamma: [{X}, {Y}] -> {Z}"

    # Graded anti-symmetry: c_{YX}^Z = -(-1)^{pX pY} c_{XY}^Z
    for (X, Y, Z), coeff in table.items():
        pX, pY = parity[X], parity[Y]
        sign = -1 if (pX * pY) % 2 == 1 else 1
        expected_coeff_yx = -sign * coeff
        actual_coeff_yx = table.get((Y, X, Z), Fraction(0))
        assert actual_coeff_yx == expected_coeff_yx, (
            f"Graded anti-symmetry violated for evaluated [{X}, {Y}] vs [{Y}, {X}] on {Z}"
        )
