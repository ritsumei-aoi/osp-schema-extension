import json
import re
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

import pytest

from src.C_evaluate import build_evaluated_schema


ROOT = Path(__file__).resolve().parent.parent


def _evaluate_expression(expression):
    coefficients = defaultdict(Fraction)
    for term in re.findall(r"[+-]?[^+-]+", expression.replace(" ", "")):
        sign = -1 if term.startswith("-") else 1
        body = term[1:] if term[:1] in "+-" else term
        if "*" in body:
            rational, parameter = body.split("*", 1)
            coefficient = Fraction(rational)
        else:
            parameter = body
            coefficient = Fraction(1)
        coefficients[parameter] += sign * coefficient
    return sum(coefficients.values(), Fraction())


def _load_pair(n):
    schema1 = json.loads((ROOT / f"data/C_{n}_structure.json").read_text())
    schema2 = json.loads((ROOT / f"data/C_{n}_gamma.json").read_text())
    return schema1, schema2


@pytest.mark.parametrize("n", (1, 2, 3))
def test_evaluated_schema_substitutes_all_positive_profile(n):
    schema1, schema2 = _load_pair(n)
    evaluated = build_evaluated_schema(
        n,
        schema1,
        schema2,
        generation_date=schema2["metadata"]["generation_date"],
    )
    parameters = schema2["gb_matrix"]["parameter_order"]
    assert evaluated["schema_layer"] == 3
    assert evaluated["source_schema"] == f"C_{n}_structure.json"
    assert evaluated["source_gamma_schema"] == f"C_{n}_gamma.json"
    assert evaluated["gb_assignment"]["profile"] == "uniform_all_positive"
    assert evaluated["gb_assignment"]["parameter_order"] == parameters
    assert evaluated["gb_assignment"]["values"] == {
        parameter: 1 for parameter in parameters
    }
    assert evaluated["structure_constants"] == schema1["structure_constants"]

    expected = []
    for record in schema2["inhomogeneous_deformation"]["gamma_structure"]:
        coefficient = _evaluate_expression(record["coeff"])
        if coefficient:
            expected.append(
                {
                    "X": record["X"],
                    "Y": record["Y"],
                    "Z": record["Z"],
                    "coeff": str(coefficient),
                    "sign_rule": record["sign_rule"],
                }
            )
    assert evaluated["inhomogeneous_deformation"]["gamma_structure"] == expected
    assert all(
        re.fullmatch(r"-?\d+(?:/\d+)?", record["coeff"])
        for record in evaluated["inhomogeneous_deformation"]["gamma_structure"]
    )


def test_evaluated_schema_rejects_unknown_parameter():
    schema1, schema2 = _load_pair(1)
    schema2["inhomogeneous_deformation"]["gamma_structure"][0]["coeff"] = (
        "gb_unknown"
    )
    with pytest.raises(ValueError, match="unknown gb parameter"):
        build_evaluated_schema(1, schema1, schema2)
