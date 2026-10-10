import json
from fractions import Fraction
from pathlib import Path

import pytest

from src.C_evaluated_generator import checkerboard_assignment, evaluate_schema


@pytest.mark.parametrize("n", [1, 2, 3])
def test_checkerboard_profile_covers_all_gb_parameters(n):
    values, assignments = checkerboard_assignment(n)

    assert len(values) == 2
    assert all(len(row) == 2 * n for row in values)
    assert len(assignments) == 4 * n
    assert set(assignments.values()) == {-1, 1}
    for row in range(2):
        for column in range(2 * n):
            assert values[row][column] == (1 if (row + column) % 2 == 0 else -1)


@pytest.mark.parametrize("n", [1, 2, 3])
def test_evaluation_substitutes_gamma_and_preserves_schema1(n):
    data_dir = Path("data")
    structure = json.loads(
        (data_dir / f"C_{n}_structure.json").read_text(encoding="utf-8")
    )
    gamma = json.loads(
        (data_dir / f"C_{n}_gamma.json").read_text(encoding="utf-8")
    )
    evaluated = evaluate_schema(n, structure, gamma, generation_date="2026-01-01")

    assert evaluated["source_files"] == {
        "structure": f"C_{n}_structure.json",
        "gamma": f"C_{n}_gamma.json",
    }
    assert evaluated["gb_assignment"]["profile"] == "checkerboard"
    assert evaluated["gb_assignment"]["values"] == checkerboard_assignment(n)[0]

    base = {
        (entry["X"], entry["Y"], entry["Z"]): Fraction(entry["coeff"])
        for entry in structure["structure_constants"]
    }
    combined = {
        (entry["X"], entry["Y"], entry["Z"]): Fraction(entry["coeff"])
        for entry in evaluated["evaluated_structure_constants"]
    }
    for key, coefficient in base.items():
        assert combined.get(key, Fraction(0)) == coefficient

    evaluated_gamma = {
        (entry["X"], entry["Y"], entry["Z"]): Fraction(entry["coeff"])
        for entry in evaluated["evaluated_gamma_coefficients"]
    }
    structure_gamma = {
        (entry["X"], entry["Y"], entry["Z"]): Fraction(entry["kappa_coeff"])
        for entry in evaluated["evaluated_structure_constants"]
    }
    assert {
        key: coefficient
        for key, coefficient in structure_gamma.items()
        if coefficient
    } == evaluated_gamma
    assert all(
        Fraction(entry["coeff"]) or Fraction(entry["kappa_coeff"])
        for entry in evaluated["evaluated_structure_constants"]
    )
    assert all(
        entry["sign_rule"] == "graded"
        for entry in evaluated["evaluated_gamma_coefficients"]
    )


def test_evaluated_gamma_coefficients_are_numeric():
    data_dir = Path("data")
    structure = json.loads((data_dir / "C_1_structure.json").read_text(encoding="utf-8"))
    gamma = json.loads((data_dir / "C_1_gamma.json").read_text(encoding="utf-8"))
    evaluated = evaluate_schema(1, structure, gamma)

    assert evaluated["evaluated_gamma_coefficients"]
    assert all(
        not any(char.isalpha() for char in entry["coeff"])
        for entry in evaluated["evaluated_gamma_coefficients"]
    )
