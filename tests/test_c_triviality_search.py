import json
from fractions import Fraction
from pathlib import Path

import pytest

from src.C_triviality_search import analyze_rank
from src.C_evaluate_structure import evaluate_schema

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("n", [1, 2, 3])
def test_triviality_conditions_and_scalar_obstructions(n):
    report = analyze_rank(n)
    zero_evaluation = evaluate_schema(n, assignment_value=0)
    parameters = report["parameters"]
    conditions = report["independent_conditions"]
    assert len(parameters) == 4 * n
    assert len(conditions) == 4 * n
    assert {
        next(iter(equation))
        for _, equation in conditions
        if len(equation) == 1 and next(iter(equation.values())) == 1
    } == set(range(len(parameters)))
    assert report["all_positive_residual"]
    assert report["trivial_profile"] is None
    assert zero_evaluation["evaluation_profile"]["name"] == "all_zero"
    assert all(
        entry["coefficients"]["kappa"] == "0"
        for entry in zero_evaluation["evaluated_structure_constants"]
    )
    structure = json.loads(
        (ROOT / "data" / f"C_{n}_structure.json").read_text(encoding="utf-8")
    )
    zero_base = {
        (entry["X"], entry["Y"], entry["Z"]): Fraction(entry["coefficients"]["constant"])
        for entry in zero_evaluation["evaluated_structure_constants"]
        if Fraction(entry["coefficients"]["constant"])
    }
    layer_one = {
        (entry["X"], entry["Y"], entry["Z"]): Fraction(entry["coeff"])
        for entry in structure["structure_constants"]
    }
    assert zero_base == layer_one
    assert len(report["scalar_witnesses"]) == 4 * n
    for witness in report["scalar_witnesses"]:
        assert witness["Z"] == "K"
        assert witness["coeff"] in ("-1", "1")

    first_parameter = report["scalar_witnesses"][0]["parameter"]
    assert report["parameter_vectors"][first_parameter]
    assert any(
        row[2] == "K" for row in report["parameter_vectors"][first_parameter]
    )


def test_rank_one_all_positive_has_explicit_coboundary_mismatch():
    report = analyze_rank(1)
    assert report["all_positive_residual"][
        ("E_eps1_del1_mm", "E_2del1_p", "K")
    ] == Fraction(-1)
