import json
from copy import deepcopy
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

import pytest

from src.C_evaluate_structure import evaluate_schema

ROOT = Path(__file__).resolve().parents[1]


@lru_cache(maxsize=None)
def evaluated_for(n):
    return evaluate_schema(n)


@pytest.mark.parametrize("n", [1, 2, 3])
def test_evaluated_schema_substitution_and_source_consistency(n):
    evaluated = evaluated_for(n)
    path = ROOT / "data" / f"C_{n}_evaluated.json"
    stored = json.loads(path.read_text(encoding="utf-8"))
    expected = deepcopy(evaluated)
    stored["metadata"].pop("generation_date")
    expected["metadata"].pop("generation_date")
    assert stored == expected

    gamma = json.loads((ROOT / "data" / f"C_{n}_gamma.json").read_text(encoding="utf-8"))
    structure = json.loads((ROOT / "data" / f"C_{n}_structure.json").read_text(encoding="utf-8"))
    assignment = evaluated["gb_assignment"]
    assert len(assignment) == 4 * n
    assert set(assignment) == {
        parameter["label"] for parameter in gamma["gb_matrix"]["parameters"]
    }
    assert set(assignment.values()) == {1}
    assert evaluated["source_structure_schema"] == f"C_{n}_structure.json"
    assert evaluated["source_gamma_schema"] == f"C_{n}_gamma.json"
    assert evaluated["coefficient_domain"] == "Q[kappa]/(kappa^2)"

    expected_coefficients = {}
    for entry in structure["structure_constants"]:
        key = (entry["X"], entry["Y"], entry["Z"])
        expected_coefficients[key] = {
            "constant": Fraction(entry["coeff"]),
            "kappa": Fraction(0),
        }
    for entry in gamma["inhomogeneous_deformation"]["gamma_coefficients"]:
        key = (entry["X"], entry["Y"], entry["Z"])
        coefficients = expected_coefficients.setdefault(
            key, {"constant": Fraction(0), "kappa": Fraction(0)}
        )
        coefficients["kappa"] += assignment[entry["parameter"]] * Fraction(entry["coeff"])

    observed = {}
    for entry in evaluated["evaluated_structure_constants"]:
        key = (entry["X"], entry["Y"], entry["Z"])
        observed[key] = {
            part: Fraction(value)
            for part, value in entry["coefficients"].items()
        }
    expected_coefficients = {
        key: values
        for key, values in expected_coefficients.items()
        if values["constant"] or values["kappa"]
    }
    assert observed == expected_coefficients
