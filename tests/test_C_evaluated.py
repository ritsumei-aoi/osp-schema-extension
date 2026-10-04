"""
Tests for Layer 3 (evaluated structure) for C(n+1) across n=1, 2, 3.
"""

import json
import pytest
from fractions import Fraction
from src.C_evaluated_generators import generate_all_schema3, evaluate_structure


@pytest.fixture(scope="module", autouse=True)
def ensure_schema3_generated():
    generate_all_schema3()


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema3_consistency_with_layers(n):
    with open(f"data/C_{n}_structure.json", "r") as f:
        s1 = json.load(f)
    with open(f"data/C_{n}_gamma.json", "r") as f:
        s2 = json.load(f)
    with open(f"data/C_{n}_evaluated.json", "r") as f:
        s3 = json.load(f)

    assert s3["schema_version"] == "5.0"
    assert s3["algebra"]["family"] == "C"
    assert s3["algebra"]["n"] == n
    assert len(s3["gb_assignment"]) == 4 * n

    # Check that when gb=1, sum of gamma matches c_kappa in s3
    gamma_sums = {}
    for entry in s2["inhomogeneous_deformation"]["gamma_structure"]:
        key = (entry["X"], entry["Y"], entry["Z"])
        gamma_sums[key] = gamma_sums.get(key, Fraction(0)) + Fraction(entry["coeff"])

    for entry in s3["evaluated_structure_constants"]:
        key = (entry["X"], entry["Y"], entry["Z"])
        c_kappa_expected = gamma_sums.get(key, Fraction(0))
        assert Fraction(entry["c_kappa"]) == c_kappa_expected
