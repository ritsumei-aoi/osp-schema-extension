import json
from fractions import Fraction
from pathlib import Path

import pytest

from src.C_evaluate import evaluate_schema

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("n", [1, 2, 3])
def test_evaluated_schema_preserves_sources_and_constants(n):
    evaluated = evaluate_schema(n)
    with (ROOT / "data" / f"C_{n}_structure.json").open(encoding="utf-8") as stream:
        structure = json.load(stream)
    with (ROOT / "data" / f"C_{n}_gamma.json").open(encoding="utf-8") as stream:
        gamma = json.load(stream)

    assert evaluated["source_schema"] == f"C_{n}_structure.json"
    assert evaluated["source_gamma"] == f"C_{n}_gamma.json"
    assert len(evaluated["gb_assignment"]["values"]) == 4 * n
    assert set(evaluated["gb_assignment"]["values"].values()) == {1}

    constants = evaluated["evaluated_structure_constants"]
    undeformed = {
        (entry["X"], entry["Y"], entry["Z"]): Fraction(entry["coeff"])
        for entry in constants if entry["kappa_order"] == 0
    }
    source = {
        (entry["X"], entry["Y"], entry["Z"]): Fraction(entry["coeff"])
        for entry in structure["structure_constants"]
    }
    assert undeformed == source

    parameters = evaluated["gb_assignment"]["values"]
    expected_gamma = {}
    for entry in gamma["inhomogeneous_deformation"]["gamma_coefficients"]:
        key = (entry["X"], entry["Y"], entry["Z"])
        expected_gamma[key] = sum(
            (
                Fraction(term["coeff"]) * parameters[term["parameter"]]
                for term in entry["coefficients"]
            ),
            Fraction(0),
        )
    actual_gamma = {
        (entry["X"], entry["Y"], entry["Z"]): Fraction(entry["coeff"])
        for entry in constants if entry["kappa_order"] == 1
    }
    assert actual_gamma == expected_gamma
