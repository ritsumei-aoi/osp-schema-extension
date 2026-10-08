import json
from copy import deepcopy
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

import pytest

from src.C_generators import build_schema


@lru_cache(maxsize=None)
def schema_for(n):
    return build_schema(n)


@pytest.mark.parametrize(
    ("n", "even_count", "odd_count"),
    [(1, 4, 4), (2, 11, 8), (3, 22, 12)],
)
def test_basis_counts_parity_and_schema(n, even_count, odd_count):
    schema = schema_for(n)
    data_path = Path(__file__).resolve().parents[1] / "data" / f"C_{n}_structure.json"
    generated_data = json.loads(data_path.read_text(encoding="utf-8"))
    expected_data = deepcopy(schema)
    generated_data["metadata"].pop("generation_date")
    expected_data["metadata"].pop("generation_date")
    assert generated_data == expected_data
    basis = schema["basis"]
    even, odd = basis["even"], basis["odd"]
    assert len(even) == even_count
    assert len(odd) == odd_count
    assert len(set(even + odd)) == even_count + odd_count
    assert schema["parity"] == {**dict.fromkeys(even, 0), **dict.fromkeys(odd, 1)}
    assert len(schema["generator_realization"]["realizations"]) == even_count + odd_count
    assert schema["algebra"]["dimension"]["total"] == even_count + odd_count
    assert len(schema["oscillator_generators"]["bosons"]["labels"]) == 2 * n
    assert schema["oscillator_generators"]["fermions"]["labels"] == ["a_1_p", "a_1_m"]
    assert schema["central_elements"]["kappa"]["parity"] == 1
    assert schema["central_elements"]["K"]["parity"] == 0


def _brackets(schema):
    parity = schema["parity"]
    labels = schema["basis"]["odd"] + schema["basis"]["even"]
    order = {label: index for index, label in enumerate(labels)}
    brackets = {}
    for entry in schema["structure_constants"]:
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        assert order[x] <= order[y]
        coefficient = Fraction(entry["coeff"])
        assert coefficient
        brackets.setdefault((x, y), {})[z] = coefficient
    return labels, parity, brackets


def _bracket(x, y, parity, brackets):
    if (x, y) in brackets:
        return brackets[x, y]
    if (y, x) not in brackets:
        return {}
    factor = -1 if parity[x] * parity[y] == 0 else 1
    return {z: factor * coefficient for z, coefficient in brackets[y, x].items()}


def _linear_combination(target, scale, source):
    for label, coefficient in source.items():
        target[label] = target.get(label, Fraction(0)) + scale * coefficient
        if not target[label]:
            del target[label]


@pytest.mark.parametrize("n", [1, 2, 3])
def test_structure_constants_are_closed_and_obey_graded_jacobi(n):
    schema = schema_for(n)
    labels, parity, brackets = _brackets(schema)
    for x in labels:
        for y in labels:
            xy = _bracket(x, y, parity, brackets)
            yx = _bracket(y, x, parity, brackets)
            factor = -1 if parity[x] * parity[y] == 0 else 1
            assert yx == {z: factor * coefficient for z, coefficient in xy.items()}
            assert all(z in labels for z in xy)

    for x in labels:
        for y in labels:
            for z in labels:
                jacobi = {}
                sign_xyz = -1 if parity[x] * parity[z] else 1
                sign_yzx = -1 if parity[y] * parity[x] else 1
                sign_zxy = -1 if parity[z] * parity[y] else 1
                for outer, inner_left, inner_right, sign in (
                    (x, y, z, sign_xyz),
                    (y, z, x, sign_yzx),
                    (z, x, y, sign_zxy),
                ):
                    for inner_label, inner_coefficient in _bracket(
                        inner_left, inner_right, parity, brackets
                    ).items():
                        _linear_combination(
                            jacobi,
                            sign * inner_coefficient,
                            _bracket(outer, inner_label, parity, brackets),
                        )
                assert not jacobi, (x, y, z, jacobi)
