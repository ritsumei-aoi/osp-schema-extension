from fractions import Fraction

import pytest

from src.C_generators import (
    _normal_order_word,
    build_schema,
    validate_schema,
)


@pytest.mark.parametrize(
    ("rank", "even_count", "odd_count", "total"),
    [(1, 4, 4, 8), (2, 11, 8, 19), (3, 22, 12, 34)],
)
def test_schema_dimensions_and_parity(rank, even_count, odd_count, total):
    schema = build_schema(rank)
    validate_schema(schema)

    assert schema["algebra"]["family"] == "C"
    assert schema["algebra"]["m"] == 1
    assert schema["algebra"]["dimension"] == {
        "even": even_count,
        "odd": odd_count,
        "total": total,
    }
    assert len(schema["basis"]["even"]) == even_count
    assert len(schema["basis"]["odd"]) == odd_count
    assert all(schema["parity"][label] == 0 for label in schema["basis"]["even"])
    assert all(schema["parity"][label] == 1 for label in schema["basis"]["odd"])


def test_standard_fermion_and_boson_normal_ordering():
    fermion = dict(_normal_order_word(("a_1_m", "a_1_p")))
    assert fermion == {
        ("a_1_p", "a_1_m"): Fraction(-1),
        (): Fraction(1),
    }

    boson = dict(_normal_order_word(("b_1_m", "b_1_p")))
    assert boson == {
        ("b_1_p", "b_1_m"): Fraction(1),
        (): Fraction(1),
    }

    assert not _normal_order_word(("a_1_p", "a_1_p"))


def test_schema_relations_and_structure_constants_are_self_consistent():
    schema = build_schema(2)
    validate_schema(schema)

    assert set(schema["oscillator_generators"]) == {"fermions", "bosons"}
    assert schema["oscillator_generators"]["fermions"]["labels"] == [
        "a_1_p",
        "a_1_m",
    ]
    assert schema["oscillator_generators"]["bosons"]["rank"] == 2
    assert schema["central_elements"]["kappa"]["parity"] == 1
    assert schema["central_elements"]["K"]["parity"] == 0
    assert schema["structure_constants"]
    assert all(
        isinstance(Fraction(entry["coeff"]), Fraction)
        and entry["sign_rule"] == "graded"
        for entry in schema["structure_constants"]
    )
    assert set(schema["generator_realization"]["realizations"]) == set(
        schema["basis"]["even"] + schema["basis"]["odd"]
    )
