import json
from fractions import Fraction
from pathlib import Path

import pytest

from src.C_generators import build_schema


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


@pytest.fixture(params=(1, 2, 3))
def generated(request):
    n = request.param
    return n, build_schema(n)


def _basis_order(schema):
    return schema["basis"]["odd"] + schema["basis"]["even"]


def _bracket_map(schema):
    parity = schema["parity"]
    result = {}
    for item in schema["structure_constants"]:
        pair = (item["X"], item["Y"])
        result.setdefault(pair, {})[item["Z"]] = Fraction(item["coeff"])
    return result


def _ordered_bracket(schema, x, y, brackets=None):
    order = _basis_order(schema)
    parity = schema["parity"]
    if brackets is None:
        brackets = _bracket_map(schema)
    if order.index(x) <= order.index(y):
        return brackets.get((x, y), {})
    sign = -1 if parity[x] * parity[y] == 0 else 1
    return {
        output: sign * coefficient
        for output, coefficient in brackets.get((y, x), {}).items()
    }


def _nested_bracket(schema, x, y, z, brackets):
    result = {}
    for intermediate, coefficient in _ordered_bracket(
        schema, y, z, brackets
    ).items():
        for output, outer_coefficient in _ordered_bracket(
            schema, x, intermediate, brackets
        ).items():
            result[output] = result.get(output, Fraction(0)) + (
                coefficient * outer_coefficient
            )
    return {key: value for key, value in result.items() if value}


def test_basis_parity_and_schema_counts(generated):
    n, schema = generated
    even = schema["basis"]["even"]
    odd = schema["basis"]["odd"]
    assert len(even) == 2 * n**2 + n + 1
    assert len(odd) == 4 * n
    assert len(set(even + odd)) == len(even) + len(odd)
    assert set(schema["parity"]) == set(even + odd)
    assert all(schema["parity"][label] == 0 for label in even)
    assert all(schema["parity"][label] == 1 for label in odd)
    assert set(schema["generator_realization"]["realizations"]) == set(even + odd)
    assert schema["algebra"]["dimension"]["total"] == 2 * n**2 + 5 * n + 1


def test_generated_files_and_structure_constant_records(generated):
    n, schema = generated
    output_path = DATA_DIR / f"C_{n}_structure.json"
    assert json.loads(output_path.read_text(encoding="utf-8")) == schema

    basis = set(_basis_order(schema))
    parity = schema["parity"]
    seen = set()
    order = _basis_order(schema)
    for item in schema["structure_constants"]:
        assert item["X"] in basis
        assert item["Y"] in basis
        assert item["Z"] in basis
        assert order.index(item["X"]) <= order.index(item["Y"])
        assert item["sign_rule"] == "graded"
        assert Fraction(item["coeff"])
        assert parity[item["Z"]] == (parity[item["X"]] + parity[item["Y"]]) % 2
        key = (item["X"], item["Y"], item["Z"])
        assert key not in seen
        seen.add(key)


def test_graded_jacobi_identity(generated):
    _, schema = generated
    labels = _basis_order(schema)
    parity = schema["parity"]
    brackets = _bracket_map(schema)
    for x in labels:
        for y in labels:
            for z in labels:
                terms = (
                    (
                        -1 if parity[x] * parity[z] else 1,
                        _nested_bracket(schema, x, y, z, brackets),
                    ),
                    (
                        -1 if parity[y] * parity[x] else 1,
                        _nested_bracket(schema, y, z, x, brackets),
                    ),
                    (
                        -1 if parity[z] * parity[y] else 1,
                        _nested_bracket(schema, z, x, y, brackets),
                    ),
                )
                total = {}
                for sign, contribution in terms:
                    for output, coefficient in contribution.items():
                        total[output] = total.get(output, Fraction(0)) + sign * coefficient
                assert all(coefficient == 0 for coefficient in total.values()), (
                    x,
                    y,
                    z,
                    total,
                )
