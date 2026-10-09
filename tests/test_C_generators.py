import json
from functools import lru_cache
from pathlib import Path

import pytest
import sympy as sp

from src.C_generators import (
    build_generators,
    build_schema,
    output_path,
)


EXPECTED_EVEN = {
    1: [
        "H_1",
        "H_2",
        "E_2del1_p",
        "E_2del1_m",
    ],
    2: [
        "H_1",
        "H_2",
        "H_3",
        "E_2del1_p",
        "E_2del2_p",
        "E_del1_del2_pp",
        "E_del1_del2_pm",
        "E_2del1_m",
        "E_2del2_m",
        "E_del1_del2_mp",
        "E_del1_del2_mm",
    ],
    3: [
        "H_1",
        "H_2",
        "H_3",
        "H_4",
        "E_2del1_p",
        "E_2del2_p",
        "E_2del3_p",
        "E_del1_del2_pp",
        "E_del1_del2_pm",
        "E_del1_del3_pp",
        "E_del1_del3_pm",
        "E_del2_del3_pp",
        "E_del2_del3_pm",
        "E_2del1_m",
        "E_2del2_m",
        "E_2del3_m",
        "E_del1_del2_mp",
        "E_del1_del2_mm",
        "E_del1_del3_mp",
        "E_del1_del3_mm",
        "E_del2_del3_mp",
        "E_del2_del3_mm",
    ],
}
EXPECTED_ODD = {
    n: [
        f"E_eps1_del{index}_{suffix}"
        for index in range(1, n + 1)
        for suffix in ("pp", "pm", "mp", "mm")
    ]
    for n in (1, 2, 3)
}
EXPECTED_DIMENSIONS = {1: (4, 4, 8), 2: (11, 8, 19), 3: (22, 12, 34)}


@pytest.fixture(scope="module")
def schemas():
    return {n: build_schema(n, generation_date="2026-10-09") for n in (1, 2, 3)}


@pytest.fixture(scope="module")
def bracket_maps(schemas):
    result = {}
    for n, schema in schemas.items():
        brackets = {}
        for record in schema["structure_constants"]:
            pair = (record["X"], record["Y"])
            bracket = brackets.setdefault(pair, {})
            bracket[record["Z"]] = sp.Rational(record["coeff"])
        result[n] = brackets
    return result


@pytest.mark.parametrize("n", (1, 2, 3))
def test_basis_dimensions_and_pbw_order(n, schemas):
    even, odd = build_generators(n)
    schema = schemas[n]
    assert [generator.label for generator in even] == EXPECTED_EVEN[n]
    assert [generator.label for generator in odd] == EXPECTED_ODD[n]

    even_dimension, odd_dimension, total_dimension = EXPECTED_DIMENSIONS[n]
    assert len(even) == even_dimension
    assert len(odd) == odd_dimension
    assert len(even) + len(odd) == total_dimension
    assert schema["basis"]["even"] == EXPECTED_EVEN[n]
    assert schema["basis"]["odd"] == EXPECTED_ODD[n]
    assert schema["basis"]["ordering_convention"].startswith("PBW: [odd")


@pytest.mark.parametrize("n", (1, 2, 3))
def test_schema_fields_parity_realizations_and_json_round_trip(n, schemas):
    schema = schemas[n]
    even_dimension, odd_dimension, total_dimension = EXPECTED_DIMENSIONS[n]
    basis = schema["basis"]
    labels = basis["odd"] + basis["even"]

    assert schema["schema_version"] == "5.0"
    assert set(schema) == {
        "schema_version",
        "algebra",
        "oscillator_generators",
        "oscillator_relations",
        "central_elements",
        "basis",
        "parity",
        "generator_realization",
        "structure_constants",
        "metadata",
    }
    assert schema["algebra"]["m"] == 1
    assert schema["algebra"]["n"] == n
    assert schema["algebra"]["dimension"] == {
        "total": total_dimension,
        "even": even_dimension,
        "odd": odd_dimension,
        "formulas": {
            "even": "2n^2+n+1",
            "odd": "4n",
            "total": "2n^2+5n+1",
        },
    }
    assert schema["oscillator_generators"]["fermions"]["labels"] == [
        "a_1_p",
        "a_1_m",
    ]
    assert schema["oscillator_generators"]["bosons"]["count"] == 2 * n
    assert set(schema["parity"]) == set(labels)
    assert set(schema["generator_realization"]["realizations"]) == set(labels)
    assert all(schema["parity"][label] == 1 for label in basis["odd"])
    assert all(schema["parity"][label] == 0 for label in basis["even"])
    assert all(
        schema["generator_realization"]["realizations"][label]["parity"]
        == schema["parity"][label]
        for label in labels
    )
    assert schema["central_elements"]["kappa"]["parity"] == 1
    assert schema["central_elements"]["K"]["parity"] == 0
    assert json.loads(json.dumps(schema, ensure_ascii=False)) == schema
    assert output_path(n, Path("data")).as_posix() == f"data/C_{n}_structure.json"


@pytest.mark.parametrize("n", (1, 2, 3))
def test_brackets_are_complete_and_graded_skew_symmetric(n, schemas, bracket_maps):
    schema = schemas[n]
    generators = {
        generator.label: generator
        for group in build_generators(n)
        for generator in group
    }
    brackets = bracket_maps[n]
    records = schema["structure_constants"]
    keys = [(r["X"], r["Y"], r["Z"]) for r in records]

    assert len(keys) == len(set(keys))
    assert all(
        record["sign_rule"] == "graded"
        and record["X"] in generators
        and record["Y"] in generators
        and record["Z"] in generators
        and sp.Rational(record["coeff"]) != 0
        for record in records
    )
    for left in generators:
        for right in generators:
            parity_sign = -1 if generators[left].parity * generators[right].parity else 1
            expected_reverse = {
                label: -parity_sign * coefficient
                for label, coefficient in brackets.get((left, right), {}).items()
            }
            assert brackets.get((right, left), {}) == expected_reverse


def _add_scaled(target, source, scale):
    for label, coefficient in source.items():
        value = target.get(label, sp.Rational(0)) + scale * coefficient
        if value:
            target[label] = value
        else:
            target.pop(label, None)


def _bracket_with_left(left, right_combination, brackets):
    result = {}
    for right, coefficient in right_combination.items():
        _add_scaled(result, brackets.get((left, right), {}), coefficient)
    return result


def _jacobi_sum(x, y, z, brackets, parity):
    result = {}
    terms = (
        (
            -1 if parity[x] * parity[z] else 1,
            x,
            brackets.get((y, z), {}),
        ),
        (
            -1 if parity[y] * parity[x] else 1,
            y,
            brackets.get((z, x), {}),
        ),
        (
            -1 if parity[z] * parity[y] else 1,
            z,
            brackets.get((x, y), {}),
        ),
    )
    for sign, left, inner in terms:
        _add_scaled(result, _bracket_with_left(left, inner, brackets), sign)
    return result


@pytest.mark.parametrize("n", (1, 2, 3))
def test_super_jacobi_identity(n, schemas, bracket_maps):
    generators = {
        generator.label: generator
        for group in build_generators(n)
        for generator in group
    }
    labels = list(schemas[n]["basis"]["odd"] + schemas[n]["basis"]["even"])
    parity = {label: generator.parity for label, generator in generators.items()}
    brackets = bracket_maps[n]

    for x in labels:
        for y in labels:
            for z in labels:
                assert _jacobi_sum(x, y, z, brackets, parity) == {}


def test_only_supported_ranks_are_accepted():
    with pytest.raises(ValueError, match="n=1, 2, and 3"):
        build_schema(4)
