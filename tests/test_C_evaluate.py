"""
Unit tests for Schema 3 (Evaluated Structure) computation and consistency.
"""

from collections import defaultdict
from fractions import Fraction
import json
import os
import pytest
from src.C_evaluate import (
    get_profile_assignment,
    evaluate_gamma_constants,
    compute_evaluated_structure,
    generate_all_evaluated_schemas,
)
from src.C_gamma import get_gb_params


@pytest.mark.parametrize("n", [1, 2, 3])
def test_all_plus_one_profile_assignment(n):
    params = get_gb_params(n)
    assignment = get_profile_assignment(n, "all_plus_one")
    assert len(assignment) == 4 * n
    for p in params:
        assert assignment[p] == "1"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema3_consistency_with_schema1_and_schema2(n):
    # Load Schema 1 and Schema 2
    with open(f"data/C_{n}_structure.json", "r", encoding="utf-8") as f:
        schema1 = json.load(f)
    with open(f"data/C_{n}_gamma.json", "r", encoding="utf-8") as f:
        schema2 = json.load(f)

    schema3 = compute_evaluated_structure(n, profile_name="all_plus_one", schema2_data=schema2)

    # Base algebra fields must match Schema 1 exactly
    for key in (
        "schema_version",
        "algebra",
        "central_elements",
        "oscillator_generators",
        "oscillator_relations",
        "basis",
        "parity",
        "generator_realization",
        "structure_constants",
    ):
        assert schema3[key] == schema1[key], f"Schema 1 and Schema 3 mismatch for key {key} (n={n})"

    # Verify evaluated_deformation structure
    assert "evaluated_deformation" in schema3
    eval_def = schema3["evaluated_deformation"]
    assert eval_def["profile_name"] == "all_plus_one"
    assert len(eval_def["parameters_assignment"]) == 4 * n

    # Check evaluated gamma matches direct evaluation of Schema 2
    raw_gamma = schema2["inhomogeneous_deformation"]["gamma_constants"]
    expected_eval = defaultdict(Fraction)
    for term in raw_gamma:
        expected_eval[(term["X"], term["Y"], term["Z"])] += Fraction(term["coeff"]) * Fraction("1")

    expected_eval_nonzero = {k: v for k, v in expected_eval.items() if v != 0}
    assert eval_def["statistics"]["total_evaluated_gamma_terms"] == len(expected_eval_nonzero)

    actual_eval = {
        (t["X"], t["Y"], t["Z"]): Fraction(t["coeff"])
        for t in eval_def["evaluated_gamma_constants"]
    }
    assert actual_eval == expected_eval_nonzero


@pytest.mark.parametrize("n, expected_terms", [
    (1, 112),
    (2, 652),
    (3, 1840),
])
def test_evaluated_data_files(n, expected_terms):
    path = f"data/C_{n}_evaluated.json"
    assert os.path.isfile(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    eval_def = data["evaluated_deformation"]
    assert eval_def["profile_name"] == "all_plus_one"
    assert len(eval_def["parameters_assignment"]) == 4 * n
    assert len(eval_def["evaluated_gamma_constants"]) == expected_terms
    assert eval_def["statistics"]["total_evaluated_gamma_terms"] == expected_terms


def test_generate_all_evaluated_schemas_tmp(tmp_path):
    out_dir = str(tmp_path)
    generate_all_evaluated_schemas(profile_name="all_plus_one", output_dir=out_dir)
    for n in (1, 2, 3):
        path = os.path.join(out_dir, f"C_{n}_evaluated.json")
        assert os.path.isfile(path)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert data["algebra"]["cartan_type"] == f"C({n+1})"
            assert data["evaluated_deformation"]["profile_name"] == "all_plus_one"
