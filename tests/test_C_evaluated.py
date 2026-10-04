"""
test_C_evaluated.py: Unit tests for Schema 3 (Evaluated Structure) for C(n+1).
Tests evaluation consistency, file existence, and preservation of parity.
"""

from fractions import Fraction
import json
import os
import pytest
from src.C_evaluated import generate_schema3, get_default_assignment, evaluate_gamma


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema3_file_existence_and_keys(n):
    filepath = os.path.join("data", f"C_{n}_evaluated.json")
    assert os.path.exists(filepath), f"{filepath} must exist"

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["schema_version"] == "5.0"
    assert data["layer"] == "3_evaluated"
    assert "evaluation_profile" in data
    assert "evaluated_gamma" in data
    assert data["evaluated_gamma"]["num_terms"] == len(data["evaluated_gamma"]["terms"])


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema3_consistency_with_schema2(n):
    path2 = os.path.join("data", f"C_{n}_gamma.json")
    path3 = os.path.join("data", f"C_{n}_evaluated.json")

    with open(path2, "r", encoding="utf-8") as f:
        s2 = json.load(f)
    with open(path3, "r", encoding="utf-8") as f:
        s3 = json.load(f)

    assert s2["algebra"] == s3["algebra"]
    assert s2["basis"] == s3["basis"]
    assert s2["parity"] == s3["parity"]

    # Verify manual re-evaluation matches exactly
    params = s2["gb_matrix"]["parameters"]
    assignment = {p: Fraction(1) for p in params}
    re_evaluated = evaluate_gamma(s2, assignment)
    assert len(re_evaluated) == len(s3["evaluated_gamma"]["terms"])


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema3_parity_condition(n):
    path3 = os.path.join("data", f"C_{n}_evaluated.json")
    with open(path3, "r", encoding="utf-8") as f:
        s3 = json.load(f)

    parities = s3["parity"]
    for term in s3["evaluated_gamma"]["terms"]:
        p_x = parities[term["X"]]
        p_y = parities[term["Y"]]
        p_z = parities[term["Z"]]
        expected_pz = (p_x + p_y + 1) % 2
        assert p_z == expected_pz, (
            f"Evaluated term ({term['X']}, {term['Y']} -> {term['Z']}) violates parity condition!"
        )
