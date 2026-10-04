"""
test_C_evaluated.py: Unit tests for Schema 3 (Evaluated Structure) for C(n+1).
"""

import json
import os
import pytest
from src.C_evaluator import evaluate_gamma


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema3_json_structure_and_consistency(n):
    eval_file = f"data/C_{n}_evaluated.json"
    gamma_file = f"data/C_{n}_gamma.json"

    assert os.path.exists(eval_file), f"Missing {eval_file}"
    assert os.path.exists(gamma_file), f"Missing {gamma_file}"

    with open(eval_file, "r") as f:
        edata = json.load(f)
    with open(gamma_file, "r") as f:
        gdata = json.load(f)

    # Check top-level keys
    assert edata["schema_version"] == "5.0"
    assert edata["algebra"] == gdata["algebra"]
    assert edata["basis"] == gdata["basis"]
    assert edata["parity"] == gdata["parity"]
    assert edata["parameter_profile"] == "all_plus"
    assert len(edata["parameter_assignment"]) == 4 * n

    # Check evaluation consistency
    recomputed = evaluate_gamma(gdata)
    assert edata["evaluated_deformation"]["total_entries"] == recomputed["evaluated_deformation"]["total_entries"]
    assert edata["evaluated_deformation"]["coefficients"] == recomputed["evaluated_deformation"]["coefficients"]

    # Check graded skew-symmetry
    parities = edata["parity"]
    brackets = {}
    for entry in edata["evaluated_deformation"]["coefficients"]:
        key = (entry["X"], entry["Y"], entry["Z"])
        brackets[key] = int(entry["coeff"]) if "/" not in entry["coeff"] else float(entry["coeff"])

    all_pairs = set((entry["X"], entry["Y"]) for entry in edata["evaluated_deformation"]["coefficients"])
    for X, Y in all_pairs:
        pX = parities[X]
        pY = parities[Y]
        expected_sign = - ((-1)**(pX * pY))

        for entry in edata["evaluated_deformation"]["coefficients"]:
            if entry["X"] == X and entry["Y"] == Y:
                Z = entry["Z"]
                c_XY = brackets.get((X, Y, Z), 0)
                c_YX = brackets.get((Y, X, Z), 0)
                assert c_YX == expected_sign * c_XY, f"Skew-symmetry failed in evaluated deformation for ({X}, {Y}) -> {Z}"
