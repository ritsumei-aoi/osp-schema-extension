import json
import re
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

import pytest

from src.C_coboundary import build_coboundary_schema


ROOT = Path(__file__).resolve().parent.parent


def _load_schema1(n):
    return json.loads((ROOT / f"data/C_{n}_structure.json").read_text())


def _parse_expression(expression):
    result = defaultdict(Fraction)
    compact = expression.replace(" ", "")
    position = 0
    token = re.compile(r"([+-]?)(?:(\d+(?:/\d+)?)\*)?(phi_[A-Za-z0-9_]+)")
    while position < len(compact):
        match = token.match(compact, position)
        assert match is not None
        sign, magnitude, parameter = match.groups()
        coefficient = Fraction(magnitude or "1")
        result[parameter] += -coefficient if sign == "-" else coefficient
        position = match.end()
    return {name: coefficient for name, coefficient in result.items() if coefficient}


def _bracket_table(schema1):
    result = defaultdict(dict)
    for record in schema1["structure_constants"]:
        result[(record["X"], record["Y"])][record["Z"]] = Fraction(
            record["coeff"]
        )
    return result


def _direct_coefficient(schema1, x, y, z):
    parity = schema1["parity"]
    brackets = _bracket_table(schema1)
    px, py = parity[x], parity[y]
    result = defaultdict(Fraction)

    for output in schema1["basis"]["odd"] + schema1["basis"]["even"]:
        if parity[output] != py:
            coefficient = brackets.get((x, output), {}).get(z, Fraction())
            result[f"phi_{output}_from_{y}"] += (-1 if px else 1) * coefficient
        if parity[output] != px:
            coefficient = brackets.get((y, output), {}).get(z, Fraction())
            sign = -1 if ((px + 1) * py) % 2 == 0 else 1
            result[f"phi_{output}_from_{x}"] += sign * coefficient

    for intermediate, coefficient in brackets.get((x, y), {}).items():
        if parity[z] != parity[intermediate]:
            result[f"phi_{z}_from_{intermediate}"] -= coefficient

    return {name: value for name, value in result.items() if value}


@pytest.mark.parametrize(
    "n,expected_parameter_count",
    ((1, 32), (2, 176), (3, 528)),
)
def test_schema4_parameterization_and_generated_file(n, expected_parameter_count):
    schema1 = _load_schema1(n)
    generated = build_coboundary_schema(
        n, schema1, generation_date="2026-10-07"
    )
    path = ROOT / f"data/C_{n}_coboundary.json"
    checked_in = json.loads(path.read_text())

    assert generated == checked_in
    assert generated["schema_layer"] == 4
    assert generated["source_schema"] == f"C_{n}_structure.json"
    assert generated["algebra"] == schema1["algebra"]

    odd_map = generated["odd_linear_map"]
    expected_names = schema1["basis"]["odd"] + schema1["basis"]["even"]
    assert len(odd_map["coefficients"]) == expected_parameter_count
    assert odd_map["parameter_order"] == [
        entry["parameter"] for entry in odd_map["coefficients"]
    ]
    for entry in odd_map["coefficients"]:
        assert entry["parameter"] == (
            f"phi_{entry['output']}_from_{entry['input']}"
        )
        assert schema1["parity"][entry["output"]] != schema1["parity"][
            entry["input"]
        ]
    assert all(
        expected_names.index(left) <= expected_names.index(right)
        for left, right in zip(
            [entry["output"] for entry in odd_map["coefficients"]],
            [entry["output"] for entry in odd_map["coefficients"]][1:],
        )
    )


@pytest.mark.parametrize("n", (1, 2, 3))
def test_coboundary_coefficients_match_definition(n):
    schema1 = _load_schema1(n)
    generated = build_coboundary_schema(
        n, schema1, generation_date="2026-10-07"
    )
    actual = {
        (record["X"], record["Y"], record["Z"]): _parse_expression(record["coeff"])
        for record in generated["coboundary"]["structure"]
    }
    names = schema1["basis"]["odd"] + schema1["basis"]["even"]
    if n == 1:
        pairs = [(x, y) for x in names for y in names]
    else:
        pairs = [
            (names[0], names[-1]),
            (names[-1], names[0]),
            (names[len(names) // 2], names[1]),
            (names[1], names[len(names) // 2]),
        ]

    for x, y in pairs:
        for z in names:
            key = (x, y, z)
            assert actual.get(key, {}) == _direct_coefficient(schema1, x, y, z)


@pytest.mark.parametrize("n", (1, 2, 3))
def test_coboundary_parity_and_graded_skew_symmetry(n):
    schema1 = _load_schema1(n)
    generated = build_coboundary_schema(
        n, schema1, generation_date="2026-10-07"
    )
    parity = schema1["parity"]
    records = generated["coboundary"]["structure"]
    actual = {}
    for record in records:
        key = (record["X"], record["Y"], record["Z"])
        assert key not in actual
        assert record["sign_rule"] == "graded"
        assert record["coeff"]
        assert parity[record["Z"]] == (
            parity[record["X"]] + parity[record["Y"]] + 1
        ) % 2
        actual[key] = _parse_expression(record["coeff"])

    for (x, y, z), terms in actual.items():
        reverse = actual.get((y, x, z), {})
        sign = -1 if parity[x] * parity[y] == 0 else 1
        expected = {name: sign * value for name, value in terms.items()}
        assert reverse == expected


def test_schema4_rejects_invalid_rank_and_schema1():
    schema1 = _load_schema1(1)
    with pytest.raises(ValueError, match="Unsupported bosonic rank"):
        build_coboundary_schema(4, schema1)

    schema1["parity"].pop(schema1["basis"]["odd"][0])
    with pytest.raises(ValueError, match="inconsistent"):
        build_coboundary_schema(1, schema1)
