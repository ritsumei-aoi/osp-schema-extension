import json
from fractions import Fraction
from itertools import product

import pytest

from src.C_generators import build_basis, build_schema, generate


@pytest.mark.parametrize(
    ("n", "even_count", "odd_count"),
    [(1, 4, 4), (2, 11, 8), (3, 22, 12)],
)
def test_basis_counts_parity_and_dimensions(n, even_count, odd_count):
    even, odd = build_basis(n)
    schema = build_schema(n)

    assert len(even) == even_count
    assert len(odd) == odd_count
    assert len(set(even + odd)) == even_count + odd_count
    assert all(schema["parity"][label] == 0 for label in even)
    assert all(schema["parity"][label] == 1 for label in odd)
    assert schema["algebra"]["dimension"]["even"] == even_count
    assert schema["algebra"]["dimension"]["odd"] == odd_count
    assert len(schema["generator_realization"]["realizations"]) == even_count + odd_count


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema_shape_and_structure_constants(n):
    schema = build_schema(n)
    labels = set(schema["basis"]["even"] + schema["basis"]["odd"])

    assert schema["schema_version"] == "5.0"
    assert schema["algebra"]["family"] == "C"
    assert schema["algebra"]["m"] == 1
    assert set(schema["oscillator_generators"]) == {"fermions", "bosons"}
    assert schema["central_elements"]["kappa"]["parity"] == 1
    assert schema["central_elements"]["K"]["parity"] == 0
    assert len(schema["oscillator_generators"]["bosons"]["labels"]) == 2 * n
    assert len(schema["structure_constants"]) > 0

    for entry in schema["structure_constants"]:
        assert entry["X"] in labels
        assert entry["Y"] in labels
        assert entry["Z"] in labels
        assert entry["sign_rule"] == "graded"


def test_rank_three_structure_constants_satisfy_super_jacobi():
    schema = build_schema(3)
    labels = schema["basis"]["even"] + schema["basis"]["odd"]
    parities = schema["parity"]
    positions = {label: index for index, label in enumerate(labels)}
    stored = {}
    for entry in schema["structure_constants"]:
        stored.setdefault((entry["X"], entry["Y"]), {})[entry["Z"]] = Fraction(entry["coeff"])

    def bracket(x, y):
        if positions[x] <= positions[y]:
            return stored.get((x, y), {})
        sign = -1 if parities[x] * parities[y] else 1
        return {z: -sign * value for z, value in stored.get((y, x), {}).items()}

    def nested(x, y, z):
        result = {}
        for inner, inner_coeff in bracket(y, z).items():
            for output, outer_coeff in bracket(x, inner).items():
                result[output] = result.get(output, Fraction(0)) + inner_coeff * outer_coeff
        return {label: value for label, value in result.items() if value}

    for x, y, z in product(labels, repeat=3):
        sign_xz = -1 if parities[x] * parities[z] else 1
        sign_xy = -1 if parities[x] * parities[y] else 1
        sign_yz = -1 if parities[y] * parities[z] else 1
        terms = [
            (sign_xz, nested(x, y, z)),
            (sign_xy, nested(y, z, x)),
            (sign_yz, nested(z, x, y)),
        ]
        total = {}
        for sign, term in terms:
            for output, value in term.items():
                total[output] = total.get(output, Fraction(0)) + sign * value
        assert all(value == 0 for value in total.values()), (x, y, z, total)


def test_generate_writes_valid_json(tmp_path):
    path = generate(1, tmp_path)
    parsed = json.loads(path.read_text(encoding="utf-8"))

    assert path.name == "C_1_structure.json"
    assert parsed == build_schema(1)
