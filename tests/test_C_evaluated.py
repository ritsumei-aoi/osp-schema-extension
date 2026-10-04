"""
Unit tests for C(n+1) Schema 3 (evaluated structure) generator.
"""

from fractions import Fraction
import json
import os
import pytest
from src.C_evaluate_deformation import evaluate_schema_3


@pytest.mark.parametrize("n", [1, 2, 3])
def test_evaluated_schema_keys_and_structure(n):
    schema = evaluate_schema_3(n)
    assert schema["schema_version"] == "5.0"
    assert "algebra" in schema
    assert "gb_assignment" in schema
    assert len(schema["gb_assignment"]) == 4 * n
    assert "evaluated_brackets" in schema
    assert len(schema["evaluated_brackets"]) > 0


@pytest.mark.parametrize("n", [1, 2, 3])
def test_evaluated_data_consistency_with_schema_1_and_2(n):
    with open(os.path.join("data", f"C_{n}_structure.json"), "r", encoding="utf-8") as f:
        s1 = json.load(f)
    with open(os.path.join("data", f"C_{n}_gamma.json"), "r", encoding="utf-8") as f:
        s2 = json.load(f)
    with open(os.path.join("data", f"C_{n}_evaluated.json"), "r", encoding="utf-8") as f:
        s3 = json.load(f)

    # Check that for any entry in s3, coeff_unperturbed matches s1
    s1_map = {(item["X"], item["Y"], item["Z"]): Fraction(item["coeff"]) for item in s1["structure_constants"]}
    s2_gamma_sum = {}
    for item in s2["inhomogeneous_deformation"]["gamma_structure"]:
        key = (item["X"], item["Y"], item["Z"])
        s2_gamma_sum[key] = s2_gamma_sum.get(key, Fraction(0)) + Fraction(item["coeff"])

    for item in s3["evaluated_brackets"]:
        key = (item["X"], item["Y"], item["Z"])
        c0 = Fraction(item["coeff_unperturbed"])
        ck = Fraction(item["coeff_kappa"])
        assert c0 == s1_map.get(key, Fraction(0))
        assert ck == s2_gamma_sum.get(key, Fraction(0))
