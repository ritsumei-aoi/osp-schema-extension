import json
from itertools import product

import pytest

from src.C_generators import build_generators, build_schema


@pytest.mark.parametrize("n", [1, 2, 3])
def test_basis_parity_and_schema_counts(n):
    even, odd, realizations, parity = build_generators(n)
    schema = build_schema(n)
    assert len(even) == 2 * n**2 + n + 1
    assert len(odd) == 4 * n
    assert len(parity) == len(even) + len(odd)
    assert set(parity) == set(realizations)
    assert all(parity[label] == 0 for label in even)
    assert all(parity[label] == 1 for label in odd)
    assert schema["algebra"]["dimension"]["even"] == len(even)
    assert schema["algebra"]["dimension"]["odd"] == len(odd)
    assert schema["algebra"]["dimension"]["total"] == len(even) + len(odd)
    assert set(schema["parity"]) == set(even + odd)
    assert len(schema["generator_realization"]["realizations"]) == len(even) + len(odd)
    assert schema["central_elements"]["kappa"]["parity"] == 1
    assert schema["central_elements"]["K"]["parity"] == 0


def test_structure_constants_match_schema_and_have_unique_ordered_pairs():
    schema = build_schema(2)
    labels = schema["basis"]["odd"] + schema["basis"]["even"]
    index = {label: position for position, label in enumerate(labels)}
    pairs = [(item["X"], item["Y"]) for item in schema["structure_constants"]]
    assert all(index[x] <= index[y] for x, y in pairs)
    assert all(item["sign_rule"] == "graded" for item in schema["structure_constants"])
    assert all(item["X"] in index and item["Y"] in index and item["Z"] in index
               for item in schema["structure_constants"])
    assert all(item["coeff"] != "0" for item in schema["structure_constants"])
    assert schema["oscillator_generators"]["fermions"]["labels"] == ["a_1_p", "a_1_m"]
    json.dumps(schema)


@pytest.mark.parametrize("n", [1, 2, 3])
def test_super_jacobi_identity(n):
    schema = build_schema(n)
    labels = schema["basis"]["odd"] + schema["basis"]["even"]
    parity = schema["parity"]
    brackets = {}
    for item in schema["structure_constants"]:
        pair = (item["X"], item["Y"])
        brackets.setdefault(pair, {}).setdefault(item["Z"], 0)
        brackets[pair][item["Z"]] += _fraction(item["coeff"])

    def bracket(x, y):
        if labels.index(x) <= labels.index(y):
            return brackets.get((x, y), {})
        result = brackets.get((y, x), {})
        sign = -1 if not (parity[x] and parity[y]) else 1
        return {z: sign * coeff for z, coeff in result.items()}

    for x, y, z in product(labels, repeat=3):
        jacobi = {}
        terms = (
            (bracket(x, y), z, (-1) ** (parity[x] * parity[z])),
            (bracket(y, z), x, (-1) ** (parity[y] * parity[x])),
            (bracket(z, x), y, (-1) ** (parity[z] * parity[y])),
        )
        for inner, outer, sign in terms:
            for middle, coeff in inner.items():
                for result, outer_coeff in bracket(middle, outer).items():
                    jacobi[result] = jacobi.get(result, 0) + sign * coeff * outer_coeff
        assert all(coeff == 0 for coeff in jacobi.values()), (n, x, y, z, jacobi)


def _fraction(value):
    from fractions import Fraction

    return Fraction(value)
