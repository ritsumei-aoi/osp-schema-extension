import json
import re
from fractions import Fraction
from pathlib import Path

import pytest

from src.C_evaluate import (
    _parse_linear_coefficient,
    evaluate_schema,
)
from src.C_generators import build_basis


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def _read_inputs(n):
    schema1 = json.loads(
        (DATA_DIR / f"C_{n}_structure.json").read_text(encoding="utf-8")
    )
    schema2 = json.loads(
        (DATA_DIR / f"C_{n}_gamma.json").read_text(encoding="utf-8")
    )
    return schema1, schema2


def _parse_test_expression(expression, values):
    parts = re.split(r" ([+-]) ", expression)
    result = Fraction()
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
        result += sign * coefficient * values[parameter]
    return result


@pytest.mark.parametrize(
    ("n", "expected_values"),
    [
        (1, [[1, -1], [-1, 1]]),
        (2, [[1, -1, -1, 1], [-1, 1, 1, -1]]),
        (3, [[1, -1, -1, 1, 1, -1], [-1, 1, 1, -1, -1, 1]]),
    ],
)
def test_checkerboard_profile_values(n, expected_values):
    schema1, schema2 = _read_inputs(n)
    evaluated = evaluate_schema(schema1, schema2, generation_date="2026-10-11")
    assert evaluated["gb_matrix"]["values"] == expected_values
    assert evaluated["parameter_profile"]["name"] == "alternating_checkerboard"


def test_exact_linear_expression_evaluation():
    values = {"gb_a1_p_b1_p": 1, "gb_a1_m_b2_m": -1}
    assert _parse_linear_coefficient(
        "2*gb_a1_p_b1_p - 1/2*gb_a1_m_b2_m",
        values,
    ) == Fraction(5, 2)
    assert _parse_linear_coefficient("-gb_a1_p_b1_p", values) == -1
    assert _parse_linear_coefficient(
        "gb_a1_p_b1_p - gb_a1_p_b1_p",
        values,
    ) == 0


def test_unknown_gb_parameter_is_rejected():
    with pytest.raises(ValueError, match="Unknown gb parameter"):
        _parse_linear_coefficient("gb_unknown", {})


@pytest.mark.parametrize("n", [1, 2, 3])
def test_checked_in_evaluated_schema_matches_generator(n):
    schema1, schema2 = _read_inputs(n)
    generated = evaluate_schema(schema1, schema2, generation_date="2026-10-11")
    checked_in = json.loads(
        (DATA_DIR / f"C_{n}_evaluated.json").read_text(encoding="utf-8")
    )
    assert checked_in == generated


@pytest.mark.parametrize("n", [1, 2, 3])
def test_evaluated_records_preserve_schema1_and_schema2_coefficients(n):
    schema1, schema2 = _read_inputs(n)
    evaluated = json.loads(
        (DATA_DIR / f"C_{n}_evaluated.json").read_text(encoding="utf-8")
    )
    parameter_values = {
        parameter: evaluated["gb_matrix"]["values"][row_index][column_index]
        for row_index, row in enumerate(evaluated["gb_matrix"]["parameters"])
        for column_index, parameter in enumerate(row)
    }
    base = {
        (record["X"], record["Y"], record["Z"]): Fraction(record["coeff"])
        for record in schema1["structure_constants"]
    }
    gamma = {
        (record["X"], record["Y"], record["Z"]): _parse_test_expression(
            record["coeff"],
            parameter_values,
        )
        for record in schema2["inhomogeneous_deformation"]["gamma_structure"]
    }
    actual = {
        (record["X"], record["Y"], record["Z"]): (
            Fraction(record["base_coeff"]),
            Fraction(record["kappa_coeff"]),
        )
        for record in evaluated["evaluated_structure_constants"]
    }
    expected_keys = {
        key for key, coefficient in base.items() if coefficient
    } | {
        key for key, coefficient in gamma.items() if coefficient
    }

    assert set(actual) == expected_keys
    for key, (base_coefficient, kappa_coefficient) in actual.items():
        assert base_coefficient == base.get(key, Fraction())
        assert kappa_coefficient == gamma.get(key, Fraction())
        assert base_coefficient or kappa_coefficient


@pytest.mark.parametrize("n", [1, 2, 3])
def test_evaluated_coefficients_obey_parity_and_graded_skew(n):
    schema1, _ = _read_inputs(n)
    evaluated = json.loads(
        (DATA_DIR / f"C_{n}_evaluated.json").read_text(encoding="utf-8")
    )
    basis = build_basis(n)
    output_parity = {**basis.parity, "K": 0}
    records = {
        (record["X"], record["Y"], record["Z"]): (
            Fraction(record["base_coeff"]),
            Fraction(record["kappa_coeff"]),
        )
        for record in evaluated["evaluated_structure_constants"]
    }

    for (x, y, z), (base_coefficient, kappa_coefficient) in records.items():
        if base_coefficient:
            assert output_parity[z] == (
                basis.parity[x] + basis.parity[y]
            ) % 2
        if kappa_coefficient:
            assert output_parity[z] == (
                basis.parity[x] + basis.parity[y] + 1
            ) % 2

    for x in basis.pbw_order:
        for y in basis.pbw_order:
            factor = -1 if basis.parity[x] * basis.parity[y] == 0 else 1
            for z in set(basis.pbw_order) | {"K"}:
                base_xy, kappa_xy = records.get(
                    (x, y, z), (Fraction(), Fraction())
                )
                base_yx, kappa_yx = records.get(
                    (y, x, z), (Fraction(), Fraction())
                )
                assert base_xy == factor * base_yx
                assert kappa_xy == factor * kappa_yx

    assert evaluated["metadata"]["source_schema1_file"] == f"C_{n}_structure.json"
    assert evaluated["metadata"]["source_schema2_file"] == f"C_{n}_gamma.json"
