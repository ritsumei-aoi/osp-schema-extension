import sys
from fractions import Fraction
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from C_generators import build_schema


@pytest.mark.parametrize(
    ("n", "even_count", "odd_count"),
    [(1, 4, 4), (2, 11, 8), (3, 22, 12)],
)
def test_basis_counts_and_parities(n, even_count, odd_count):
    schema = build_schema(n)
    even = schema["basis"]["even"]
    odd = schema["basis"]["odd"]

    assert len(even) == even_count
    assert len(odd) == odd_count
    assert len(set(even + odd)) == even_count + odd_count
    assert all(schema["parity"][label] == 0 for label in even)
    assert all(schema["parity"][label] == 1 for label in odd)
    assert set(schema["parity"]) == set(even + odd)
    assert schema["algebra"]["dimension"]["even"] == even_count
    assert schema["algebra"]["dimension"]["odd"] == odd_count


@pytest.mark.parametrize("n", [1, 2, 3])
def test_structure_constants_are_closed_and_schema_complete(n):
    schema = build_schema(n)
    generators = set(schema["basis"]["even"] + schema["basis"]["odd"])

    assert schema["schema_version"] == "5.0"
    assert set(schema) == {
        "schema_version", "algebra", "oscillator_generators",
        "oscillator_relations", "central_elements", "basis", "parity",
        "generator_realization", "structure_constants", "metadata",
    }
    assert schema["central_elements"]["kappa"]["parity"] == 1
    assert schema["central_elements"]["K"]["parity"] == 0
    for bracket in schema["structure_constants"]:
        assert bracket["X"] in generators
        assert bracket["Y"] in generators
        assert bracket["Z"] in generators
        assert bracket["coeff"] != "0"
        assert bracket["sign_rule"] == "graded"

    parity = schema["parity"]
    constants = {
        (item["X"], item["Y"], item["Z"]): Fraction(item["coeff"])
        for item in schema["structure_constants"]
    }
    for (x, y, z), coefficient in constants.items():
        sign = -1 if parity[x] * parity[y] % 2 == 0 else 1
        assert constants[(y, x, z)] == sign * coefficient


def test_invalid_rank_is_rejected():
    with pytest.raises(ValueError, match="positive integer"):
        build_schema(0)
