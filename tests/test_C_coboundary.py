import json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

import pytest

from src.C_coboundary import build_coboundary_schema, output_path


@pytest.fixture(scope="module")
def coboundary_schemas():
    return {
        n: build_coboundary_schema(n, generation_date="2026-10-09")
        for n in (1, 2, 3)
    }


def _parse_polynomial(expression: str) -> dict[str, Fraction]:
    result: dict[str, Fraction] = {}
    for piece in expression.replace("- ", "+ -").split(" + "):
        piece = piece.strip()
        sign = -1 if piece.startswith("-") else 1
        term = piece[1:] if sign < 0 else piece
        if "*" in term:
            coefficient_text, parameter = term.split("*", 1)
            coefficient = Fraction(coefficient_text)
        else:
            coefficient, parameter = Fraction(1), term
        result[parameter] = result.get(parameter, Fraction(0)) + sign * coefficient
    return {parameter: coefficient for parameter, coefficient in result.items() if coefficient}


def _direct_delta_f(
    left: str,
    right: str,
    parity: dict[str, int],
    brackets: dict[tuple[str, str], dict[str, Fraction]],
    f_values: dict[str, dict[str, Fraction]],
) -> dict[str, Fraction]:
    result: dict[str, Fraction] = defaultdict(Fraction)
    first_scale = -1 if parity[left] else 1
    second_exponent = (parity[left] + 1) * parity[right]
    second_scale = -1 if second_exponent % 2 == 0 else 1
    for map_output, value in f_values[right].items():
        for output, coefficient in brackets.get((left, map_output), {}).items():
            result[output] += first_scale * coefficient * value
    for map_output, value in f_values[left].items():
        for output, coefficient in brackets.get((right, map_output), {}).items():
            result[output] += second_scale * coefficient * value
    for bracket_output, coefficient in brackets.get((left, right), {}).items():
        for output, value in f_values[bracket_output].items():
            result[output] -= coefficient * value
    return {output: value for output, value in result.items() if value}


@pytest.mark.parametrize("n", (1, 2, 3))
def test_general_odd_map_has_exactly_all_parity_reversing_entries(n, coboundary_schemas):
    schema = coboundary_schemas[n]
    entries = schema["coboundary"]["odd_linear_map"]["entries"]
    parity = schema["parity"]
    expected_count = 2 * len(schema["basis"]["even"]) * len(schema["basis"]["odd"])

    assert len(entries) == expected_count
    assert len({entry["parameter"] for entry in entries}) == expected_count
    assert all(parity[entry["input"]] != parity[entry["output"]] for entry in entries)
    assert all(
        entry["parameter"] == f"phi_{entry['output']}_from_{entry['input']}"
        for entry in entries
    )


@pytest.mark.parametrize("n", (1, 2, 3))
def test_delta_f_matches_direct_exact_formula(n, coboundary_schemas):
    schema = coboundary_schemas[n]
    labels = schema["basis"]["odd"] + schema["basis"]["even"]
    parity = schema["parity"]
    brackets: dict[tuple[str, str], dict[str, Fraction]] = defaultdict(dict)
    for record in schema["structure_constants"]:
        brackets[(record["X"], record["Y"])][record["Z"]] = Fraction(record["coeff"])

    map_entries = schema["coboundary"]["odd_linear_map"]["entries"]
    f_values: dict[str, dict[str, Fraction]] = defaultdict(dict)
    parameter_values = {}
    for index, entry in enumerate(map_entries, start=1):
        value = Fraction(index % 5 - 2)
        parameter_values[entry["parameter"]] = value
        f_values[entry["input"]][entry["output"]] = value

    output_records = schema["coboundary"]["delta_f_coefficients"]
    serialized = {
        (record["X"], record["Y"]): defaultdict(dict)
        for record in output_records
    }
    for record in output_records:
        serialized[(record["X"], record["Y"])][record["Z"]] = _parse_polynomial(
            record["coeff"]
        )

    for left in labels:
        for right in labels:
            expected = _direct_delta_f(left, right, parity, brackets, f_values)
            actual = {
                output: sum(
                    coefficient * parameter_values[parameter]
                    for parameter, coefficient in polynomial.items()
                )
                for output, polynomial in serialized.get((left, right), {}).items()
            }
            actual = {output: value for output, value in actual.items() if value}
            assert actual == expected


@pytest.mark.parametrize("n", (1, 2, 3))
def test_delta_f_outputs_have_expected_basis_parity(n, coboundary_schemas):
    schema = coboundary_schemas[n]
    parity = schema["parity"]
    basis_labels = set(schema["basis"]["even"] + schema["basis"]["odd"])
    records = schema["coboundary"]["delta_f_coefficients"]

    assert all(record["X"] in basis_labels for record in records)
    assert all(record["Y"] in basis_labels for record in records)
    assert all(record["Z"] in basis_labels for record in records)
    assert all(
        parity[record["Z"]] == (parity[record["X"]] ^ parity[record["Y"]] ^ 1)
        for record in records
    )
    assert all(record["sign_rule"] == "graded" for record in records)
    assert all(_parse_polynomial(record["coeff"]) for record in records)


@pytest.mark.parametrize("n", (1, 2, 3))
def test_central_k_components_are_preserved_as_unmatched(n, coboundary_schemas):
    schema = coboundary_schemas[n]
    target = json.loads((Path("data") / f"C_{n}_evaluated.json").read_text())
    expected = [
        record
        for record in target["inhomogeneous_deformation"]["evaluated_gamma_coefficients"]
        if record["Z"] == "K"
    ]
    comparison = schema["coboundary"]["comparison"]

    assert comparison["target_file"] == f"data/C_{n}_evaluated.json"
    assert comparison["unmatched_central_components"] == expected
    assert all(record["Z"] == "K" for record in comparison["unmatched_central_components"])


@pytest.mark.parametrize("n", (1, 2, 3))
def test_coboundary_schema_preserves_layer1_basis_and_filename(n, coboundary_schemas):
    schema = coboundary_schemas[n]
    schema1 = json.loads((Path("data") / f"C_{n}_structure.json").read_text())

    assert schema["algebra"] == schema1["algebra"]
    assert schema["basis"] == schema1["basis"]
    assert schema["parity"] == schema1["parity"]
    assert schema["structure_constants"] == schema1["structure_constants"]
    assert output_path(n, Path("data")).as_posix() == f"data/C_{n}_coboundary.json"
    assert json.loads(json.dumps(schema, ensure_ascii=False)) == schema


def test_generated_coboundary_file_matches_computed_schema(coboundary_schemas):
    for n, schema in coboundary_schemas.items():
        generated = json.loads(
            (Path("data") / f"C_{n}_coboundary.json").read_text(encoding="utf-8")
        )
        assert generated == schema
