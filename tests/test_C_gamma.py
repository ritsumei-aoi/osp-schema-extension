import json
import re
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

import pytest

from src.C_gamma import build_gamma_schema


ROOT = Path(__file__).resolve().parent.parent


def _parse_expression(expression):
    coefficients = defaultdict(Fraction)
    for term in re.findall(r"[+-]?[^+-]+", expression.replace(" ", "")):
        sign = -1 if term.startswith("-") else 1
        body = term[1:] if term[:1] in "+-" else term
        if "*" in body:
            rational, parameter = body.split("*", 1)
            coeff = Fraction(rational)
        else:
            parameter = body
            coeff = Fraction(1)
        coefficients[parameter] += sign * coeff
    return {key: value for key, value in coefficients.items() if value}


def _load_pair(n):
    schema1 = json.loads((ROOT / f"data/C_{n}_structure.json").read_text())
    schema2 = json.loads((ROOT / f"data/C_{n}_gamma.json").read_text())
    return schema1, schema2


@pytest.mark.parametrize("n", (1, 2, 3))
def test_gamma_schema_and_source_consistency(n):
    schema1, schema2 = _load_pair(n)
    generated = build_gamma_schema(
        n,
        schema1,
        generation_date=schema2["metadata"]["generation_date"],
    )
    assert generated == schema2
    assert schema2["source_schema"] == f"C_{n}_structure.json"

    matrix = schema2["gb_matrix"]
    assert matrix["rows"] == ["a_1_p", "a_1_m"]
    assert matrix["columns"] == [
        f"b_{index}_{sign}"
        for index in range(1, n + 1)
        for sign in ("p", "m")
    ]
    assert len(matrix["entries"]) == 2
    assert all(len(row) == 2 * n for row in matrix["entries"])
    assert all(
        entry["parity"] == 0
        for row in matrix["entries"]
        for entry in row
    )


@pytest.mark.parametrize("n", (1, 2, 3))
def test_gamma_coefficients_are_parity_consistent_and_graded_skew(n):
    schema1, schema2 = _load_pair(n)
    parity = schema1["parity"]
    coefficients = defaultdict(lambda: defaultdict(Fraction))
    gamma_records = schema2["inhomogeneous_deformation"]["gamma_structure"]

    for entry in gamma_records:
        assert entry["sign_rule"] == "graded"
        assert entry["Z"] == "K" or entry["Z"] in parity
        for parameter, coeff in _parse_expression(entry["coeff"]).items():
            assert parameter in schema2["gb_matrix"]["parameter_order"]
            assert coeff
            output_parity = parity.get(entry["Z"], 0)
            assert output_parity == (
                parity[entry["X"]] + parity[entry["Y"]] + 1
            ) % 2
            coefficients[(entry["X"], entry["Y"], entry["Z"])][parameter] += coeff

    generators = schema1["basis"]["odd"] + schema1["basis"]["even"]
    for left in generators:
        for right in generators:
            sign = -((-1) ** (parity[left] * parity[right]))
            outputs = {
                output
                for x, y, output in coefficients
                if (x, y) == (left, right)
            }
            reverse_outputs = {
                output
                for x, y, output in coefficients
                if (x, y) == (right, left)
            }
            for output in outputs | reverse_outputs:
                forward = coefficients[(left, right, output)]
                reverse = coefficients[(right, left, output)]
                expected = {
                    parameter: sign * coeff
                    for parameter, coeff in forward.items()
                    if coeff
                }
                assert {
                    parameter: coeff
                    for parameter, coeff in reverse.items()
                    if coeff
                } == expected


@pytest.mark.parametrize("n", (1, 2, 3))
def test_gamma_satisfies_first_order_super_jacobi(n):
    schema1, schema2 = _load_pair(n)
    parity = schema1["parity"]
    names = schema1["basis"]["odd"] + schema1["basis"]["even"]
    base = defaultdict(lambda: defaultdict(Fraction))
    for entry in schema1["structure_constants"]:
        base[(entry["X"], entry["Y"])][entry["Z"]] += Fraction(entry["coeff"])

    gamma = defaultdict(lambda: defaultdict(Fraction))
    for entry in schema2["inhomogeneous_deformation"]["gamma_structure"]:
        key = (entry["X"], entry["Y"], entry["Z"])
        for parameter, coeff in _parse_expression(entry["coeff"]).items():
            gamma[key][parameter] += coeff

    for x in names:
        for y in names:
            for z in names:
                residual = defaultdict(Fraction)
                for a, b, c in ((x, y, z), (y, z, x), (z, x, y)):
                    cyclic_sign = (-1) ** (parity[a] * parity[c])
                    for inner, inner_coeff in base[(b, c)].items():
                        for target in names + ["K"]:
                            for parameter, coeff in gamma[(a, inner, target)].items():
                                residual[parameter] += cyclic_sign * inner_coeff * coeff

                    for target in names:
                        for outer, outer_coeff in base[(a, target)].items():
                            for parameter, coeff in gamma[(b, c, target)].items():
                                residual[parameter] += (
                                    cyclic_sign
                                    * (-1) ** parity[a]
                                    * outer_coeff
                                    * coeff
                                )
                assert not any(residual.values()), (x, y, z, dict(residual))
