import json
import re
from fractions import Fraction
from pathlib import Path

import pytest

from src.C_coboundary import generate_coboundary_schema
from src.C_generators import build_basis


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
EXPECTED_COEFFICIENT_COUNTS = {1: 32, 2: 176, 3: 528}


def _read_schema1(n):
    return json.loads(
        (DATA_DIR / f"C_{n}_structure.json").read_text(encoding="utf-8")
    )


def _parse_expression(expression):
    terms = {}
    parts = re.split(r" ([+-]) ", expression)
    for index in range(0, len(parts), 2):
        sign = 1 if index == 0 or parts[index - 1] == "+" else -1
        term = parts[index]
        if index == 0 and term.startswith("-"):
            sign *= -1
            term = term[1:]
        if "*" in term:
            scalar, parameter = term.split("*", maxsplit=1)
            coefficient = Fraction(scalar)
        else:
            coefficient, parameter = Fraction(1), term
        terms[parameter] = terms.get(parameter, Fraction()) + sign * coefficient
    return {parameter: coefficient for parameter, coefficient in terms.items() if coefficient}


def _add(target, label, coefficient):
    value = target.get(label, Fraction()) + coefficient
    if value:
        target[label] = value
    else:
        target.pop(label, None)


def _direct_numeric_coboundary(schema1, schema4, phi_values):
    labels = build_basis(schema1["algebra"]["n"]).pbw_order
    parity = schema1["parity"]
    brackets = {}
    for record in schema1["structure_constants"]:
        brackets.setdefault((record["X"], record["Y"]), {})[
            record["Z"]
        ] = Fraction(record["coeff"])
    f_outputs = {}
    for coefficient in schema4["odd_linear_map"]["coefficients"]:
        f_outputs.setdefault(coefficient["input"], []).append(
            (coefficient["output"], coefficient["symbol"])
        )

    result = {}
    for x in labels:
        px = parity[x]
        for y in labels:
            py = parity[y]
            coefficients = {}
            first_scale = -1 if px else 1
            second_exponent = (px + 1) * py
            second_scale = -1 if second_exponent % 2 == 0 else 1

            for intermediate, symbol in f_outputs[y]:
                for z, coefficient in brackets.get((x, intermediate), {}).items():
                    _add(coefficients, z, first_scale * phi_values[symbol] * coefficient)

            for intermediate, symbol in f_outputs[x]:
                for z, coefficient in brackets.get((y, intermediate), {}).items():
                    _add(coefficients, z, second_scale * phi_values[symbol] * coefficient)

            for intermediate, bracket_coefficient in brackets.get((x, y), {}).items():
                for z, symbol in f_outputs.get(intermediate, []):
                    _add(
                        coefficients,
                        z,
                        -bracket_coefficient * phi_values[symbol],
                    )
            result[(x, y)] = coefficients
    return result


@pytest.mark.parametrize("n", [1, 2, 3])
def test_general_odd_map_has_all_and_only_parity_reversing_coefficients(n):
    schema1 = _read_schema1(n)
    schema4 = generate_coboundary_schema(schema1, generation_date="2026-10-11")
    basis = build_basis(n)
    coefficients = schema4["odd_linear_map"]["coefficients"]

    assert schema4["odd_linear_map"]["parity"] == 1
    assert schema4["odd_linear_map"]["coefficient_count"] == EXPECTED_COEFFICIENT_COUNTS[n]
    assert len(coefficients) == EXPECTED_COEFFICIENT_COUNTS[n]
    assert all(
        basis.parity[item["input"]] != basis.parity[item["output"]]
        for item in coefficients
    )
    assert len({item["symbol"] for item in coefficients}) == len(coefficients)


@pytest.mark.parametrize("n", [1, 2, 3])
def test_checked_in_coboundary_schema_matches_generator(n):
    schema1 = _read_schema1(n)
    generated = generate_coboundary_schema(
        schema1,
        generation_date="2026-10-11",
    )
    checked_in = json.loads(
        (DATA_DIR / f"C_{n}_coboundary.json").read_text(encoding="utf-8")
    )
    assert checked_in == generated


@pytest.mark.parametrize("n", [1, 2, 3])
def test_coboundary_outputs_have_correct_parity_and_graded_skew(n):
    schema1 = _read_schema1(n)
    schema4 = json.loads(
        (DATA_DIR / f"C_{n}_coboundary.json").read_text(encoding="utf-8")
    )
    basis = build_basis(n)
    records = {
        (record["X"], record["Y"], record["Z"]): _parse_expression(
            record["coeff"]
        )
        for record in schema4["coboundary_structure"]
    }

    for (x, y, z), coefficients in records.items():
        assert basis.parity[z] == (
            basis.parity[x] + basis.parity[y] + 1
        ) % 2
        assert coefficients

    for x in basis.pbw_order:
        for y in basis.pbw_order:
            factor = -1 if basis.parity[x] * basis.parity[y] == 0 else 1
            for z in basis.pbw_order:
                forward = records.get((x, y, z), {})
                reverse = records.get((y, x, z), {})
                assert forward == {
                    parameter: factor * coefficient
                    for parameter, coefficient in reverse.items()
                }


@pytest.mark.parametrize("n", [1, 2, 3])
def test_symbolic_coboundary_matches_direct_formula_for_numeric_maps(n):
    schema1 = _read_schema1(n)
    schema4 = json.loads(
        (DATA_DIR / f"C_{n}_coboundary.json").read_text(encoding="utf-8")
    )
    coefficients = schema4["odd_linear_map"]["coefficients"]
    phi_values = {
        item["symbol"]: Fraction((index * 7) % 5 - 2)
        for index, item in enumerate(coefficients)
    }
    expected = _direct_numeric_coboundary(schema1, schema4, phi_values)
    actual = {}
    for record in schema4["coboundary_structure"]:
        value = sum(
            (coefficient * phi_values[parameter]
             for parameter, coefficient in _parse_expression(record["coeff"]).items()),
            Fraction(),
        )
        if value:
            actual.setdefault((record["X"], record["Y"]), {})[record["Z"]] = value

    assert actual == {
        pair: values for pair, values in expected.items() if values
    }
