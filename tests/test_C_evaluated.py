from fractions import Fraction
import json
import os
import pytest

from src.C_generators import get_C_generators
from src.C_gamma import get_deformation_parameters, generate_schema_2_json
from src.C_evaluated import (
    evaluate_gamma_at_assignment,
    build_schema_3_json,
    generate_and_save_all_evaluated
)


@pytest.mark.parametrize("n", [1, 2, 3])
def test_evaluated_schema_generation(n):
    data = build_schema_3_json(n, assignment_name="all_ones")
    assert data["schema_version"] == "5.0"
    assert data["algebra"]["family"] == "C"
    assert data["algebra"]["n"] == n
    assert len(data["evaluated_parameters"]) == 4 * n
    assert len(data["evaluated_gamma_structure_constants"]) > 0


@pytest.mark.parametrize("n", [1, 2, 3])
def test_evaluated_consistency_with_schema_2(n):
    even_basis, odd_basis, parity, _, _ = get_C_generators(n)
    all_basis = odd_basis + even_basis
    gamma_data = generate_schema_2_json(n)
    params = get_deformation_parameters(n)

    # Unit assignment: gb_1 = 1, others = 0
    unit_param = params[0]
    assignment = {p: (1 if p == unit_param else 0) for p in params}

    eval_data = build_schema_3_json(n, assignment_name=f"unit_{unit_param}", custom_assignment=assignment)

    # Check each term in evaluated matches Schema 2 entry for unit_param
    schema2_map = {}
    for entry in gamma_data["gamma_structure_constants"]:
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        for item in entry["linear_combination"]:
            if item["param"] == unit_param:
                schema2_map[(x, y, z)] = Fraction(item["coeff"])

    eval_map = {}
    for entry in eval_data["evaluated_gamma_structure_constants"]:
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        eval_map[(x, y, z)] = Fraction(entry["coeff"])

    assert schema2_map == eval_map


def test_save_all_evaluated_files():
    generate_and_save_all_evaluated("data")
    for n in [1, 2, 3]:
        file_path = f"data/C_{n}_evaluated.json"
        assert os.path.exists(file_path)
        with open(file_path, "r") as f:
            d = json.load(f)
        assert d["schema_version"] == "5.0"
        assert len(d["evaluated_gamma_structure_constants"]) > 0
