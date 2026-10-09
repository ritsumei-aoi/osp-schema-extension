import json
from fractions import Fraction
from pathlib import Path

import pytest

from src.C_evaluated import build_evaluated_schema, output_path


@pytest.fixture(scope="module")
def evaluated_schemas():
    return {
        n: build_evaluated_schema(n, generation_date="2026-10-09")
        for n in (1, 2, 3)
    }


def _direct_substitution(expression: str, values: dict[str, int]) -> Fraction:
    total = Fraction(0)
    for piece in expression.replace("- ", "+ -").split(" + "):
        piece = piece.strip()
        sign = -1 if piece.startswith("-") else 1
        term = piece[1:] if sign < 0 else piece
        if "*" in term:
            coefficient_text, parameter = term.split("*", 1)
            coefficient = Fraction(coefficient_text)
        else:
            coefficient, parameter = Fraction(1), term
        total += sign * coefficient * values[parameter]
    return total


@pytest.mark.parametrize("n", (1, 2, 3))
def test_evaluated_profile_and_schema1_data_are_preserved(n, evaluated_schemas):
    evaluated = evaluated_schemas[n]
    schema1 = json.loads((Path("data") / f"C_{n}_structure.json").read_text())
    deformation = evaluated["inhomogeneous_deformation"]
    values = deformation["evaluation_profile"]["parameter_values"]

    assert deformation["evaluation_profile"]["name"] == "all_positive"
    assert len(values) == 4 * n
    assert set(values.values()) == {1}
    assert evaluated["basis"] == schema1["basis"]
    assert evaluated["parity"] == schema1["parity"]
    assert evaluated["structure_constants"] == schema1["structure_constants"]
    assert evaluated["algebra"] == schema1["algebra"]


@pytest.mark.parametrize("n", (1, 2, 3))
def test_evaluated_coefficients_match_exact_schema2_substitution(n, evaluated_schemas):
    gamma = json.loads((Path("data") / f"C_{n}_gamma.json").read_text())
    evaluated = evaluated_schemas[n]["inhomogeneous_deformation"]
    values = evaluated["evaluation_profile"]["parameter_values"]
    expected: dict[tuple[str, str, str], Fraction] = {}
    for record in gamma["inhomogeneous_deformation"]["gamma_coefficients"]:
        key = (record["X"], record["Y"], record["Z"])
        expected[key] = expected.get(key, Fraction(0)) + _direct_substitution(
            record["coeff"], values
        )
    expected = {key: value for key, value in expected.items() if value}
    actual = {
        (record["X"], record["Y"], record["Z"]): Fraction(record["coeff"])
        for record in evaluated["evaluated_gamma_coefficients"]
    }

    assert actual == expected
    assert actual
    assert any(output == "K" for _, _, output in actual)
    assert all(record["sign_rule"] == "graded" for record in evaluated["evaluated_gamma_coefficients"])


@pytest.mark.parametrize("n", (1, 2, 3))
def test_evaluated_schema_serialization_and_filename(n, evaluated_schemas):
    schema = evaluated_schemas[n]
    path = output_path(n, Path("data"))

    assert path.as_posix() == f"data/C_{n}_evaluated.json"
    assert schema["schema_version"] == "5.0"
    assert schema["metadata"]["generated_by"] == "C_evaluated.py"
    assert json.loads(json.dumps(schema, ensure_ascii=False)) == schema


def test_evaluated_records_preserve_valid_labels_and_central_identity(evaluated_schemas):
    for n, schema in evaluated_schemas.items():
        basis_labels = set(schema["basis"]["even"] + schema["basis"]["odd"])
        records = schema["inhomogeneous_deformation"]["evaluated_gamma_coefficients"]
        assert all(record["X"] in basis_labels for record in records)
        assert all(record["Y"] in basis_labels for record in records)
        assert all(record["Z"] in basis_labels | {"K"} for record in records)
        assert all(Fraction(record["coeff"]) for record in records)


def test_evaluated_file_matches_computed_schema(evaluated_schemas):
    for n, schema in evaluated_schemas.items():
        generated = json.loads(
            (Path("data") / f"C_{n}_evaluated.json").read_text(encoding="utf-8")
        )
        assert generated == schema
