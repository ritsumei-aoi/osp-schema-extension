import json
from collections import defaultdict
from fractions import Fraction

import pytest

from src.C_generators import (
    _generator_data,
    _normal_order_word,
    _solve_coordinates,
    _superbracket,
    build_schema,
    generate,
)


@pytest.fixture(scope="module")
def schemas():
    return {n: build_schema(n) for n in (1, 2, 3)}


@pytest.mark.parametrize(
    ("n", "even_count", "odd_count", "total"),
    ((1, 4, 4, 8), (2, 11, 8, 19), (3, 22, 12, 34)),
)
def test_generator_counts_and_dimensions(schemas, n, even_count, odd_count, total):
    schema = schemas[n]
    assert len(schema["basis"]["even"]) == even_count
    assert len(schema["basis"]["odd"]) == odd_count
    assert schema["algebra"]["dimension"] == {
        "total": total,
        "even": even_count,
        "odd": odd_count,
        "even_formula": "2n^2 + n + 1",
        "odd_formula": "4n",
        "total_formula": "2n^2 + 5n + 1",
    }


@pytest.mark.parametrize("n", (1, 2, 3))
def test_parity_and_basis_consistency(schemas, n):
    schema = schemas[n]
    basis = schema["basis"]
    even, odd = basis["even"], basis["odd"]
    assert len(set(even + odd)) == len(even) + len(odd)
    assert set(schema["parity"]) == set(even + odd)
    assert all(schema["parity"][label] == 0 for label in even)
    assert all(schema["parity"][label] == 1 for label in odd)
    assert len(odd) == 4 * n
    assert all(label.startswith("E_eps1_del") for label in odd)
    assert set(schema["central_elements"]) == {"kappa", "K"}
    assert schema["central_elements"]["kappa"]["parity"] == 1
    assert schema["central_elements"]["K"]["parity"] == 0


@pytest.mark.parametrize("n", (1, 2, 3))
def test_constants_match_oscillator_brackets(schemas, n):
    schema = schemas[n]
    full_order, parity, realizations = _generator_data(n)
    constants = defaultdict(dict)
    for entry in schema["structure_constants"]:
        assert entry["sign_rule"] == "graded"
        key = (entry["X"], entry["Y"])
        assert entry["Z"] not in constants[key]
        constants[key][entry["Z"]] = Fraction(entry["coeff"])

    for i, left in enumerate(full_order):
        for right in full_order[i:]:
            bracket = _superbracket(
                realizations[left],
                realizations[right],
                parity[left],
                parity[right],
            )
            expected = _solve_coordinates(full_order, realizations, bracket) if bracket else {}
            assert constants.get((left, right), {}) == expected


@pytest.mark.parametrize("n", (1, 2, 3))
def test_super_jacobi_identity(schemas, n):
    schema = schemas[n]
    parity = schema["parity"]
    order, _, _ = _generator_data(n)
    order_index = {label: index for index, label in enumerate(order)}
    brackets = defaultdict(dict)
    for entry in schema["structure_constants"]:
        brackets[(entry["X"], entry["Y"])][entry["Z"]] = Fraction(entry["coeff"])

    def bracket(left, right):
        key = (
            (left, right)
            if order_index[left] <= order_index[right]
            else (right, left)
        )
        result = brackets.get(key, {})
        if left != key[0]:
            sign = -1 if parity[left] * parity[right] % 2 else 1
            return {label: -sign * coefficient for label, coefficient in result.items()}
        return result

    def nested(left, right_result):
        result = defaultdict(Fraction)
        for right, coefficient in right_result.items():
            for label, value in bracket(left, right).items():
                result[label] += coefficient * value
        return {label: coefficient for label, coefficient in result.items() if coefficient}

    for x in order:
        for y in order:
            for z in order:
                terms = (
                    nested(x, bracket(y, z)),
                    nested(y, bracket(z, x)),
                    nested(z, bracket(x, y)),
                )
                signs = (
                    -1 if parity[x] * parity[z] % 2 else 1,
                    -1 if parity[y] * parity[x] % 2 else 1,
                    -1 if parity[z] * parity[y] % 2 else 1,
                )
                total = defaultdict(Fraction)
                for sign, term in zip(signs, terms):
                    for label, coefficient in term.items():
                        total[label] += sign * coefficient
                assert not any(total.values()), (x, y, z, dict(total))


def test_generator_writes_rank_named_json_files(tmp_path):
    paths = generate(tmp_path, (1, 2, 3))
    assert [path.name for path in paths] == [
        "C_1_structure.json",
        "C_2_structure.json",
        "C_3_structure.json",
    ]
    for path in paths:
        assert json.loads(path.read_text())["schema_version"] == "5.0"


def test_canonical_oscillator_relations():
    assert dict(_normal_order_word(("a_1_m", "a_1_p"))) == {
        (): Fraction(1),
        ("a_1_p", "a_1_m"): Fraction(-1),
    }
    assert dict(_normal_order_word(("b_1_m", "b_1_p"))) == {
        (): Fraction(1),
        ("b_1_p", "b_1_m"): Fraction(1),
    }
    assert _normal_order_word(("a_1_p", "a_1_p")) == ()


@pytest.mark.parametrize("n", (1, 2, 3))
def test_generated_data_files_follow_schema(schemas, n):
    data_path = f"data/C_{n}_structure.json"
    with open(data_path, encoding="utf-8") as file:
        committed = json.load(file)
    generated = schemas[n]
    committed["metadata"]["generation_date"] = generated["metadata"]["generation_date"]
    assert committed == generated

    assert set(generated) == {
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
    assert set(generated["generator_realization"]["realizations"]) == set(
        generated["basis"]["even"] + generated["basis"]["odd"]
    )
    order, _, _ = _generator_data(n)
    order_index = {label: index for index, label in enumerate(order)}
    assert all(
        order_index[entry["X"]] <= order_index[entry["Y"]]
        for entry in generated["structure_constants"]
    )
