from fractions import Fraction

import pytest

from src.C_generators import (
    _bracket,
    _fraction_string,
    _word_polynomial,
    build_basis,
    build_realizations,
    build_schema,
)


EXPECTED_DIMENSIONS = {
    1: (4, 4, 8),
    2: (11, 8, 19),
    3: (22, 12, 34),
}


@pytest.mark.parametrize("n,dimensions", EXPECTED_DIMENSIONS.items())
def test_basis_counts_and_parity(n, dimensions):
    basis = build_basis(n)
    even, odd = basis["even"], basis["odd"]

    assert (len(even), len(odd), len(even) + len(odd)) == dimensions
    assert len(set(even + odd)) == sum(dimensions[:2])
    assert all(name.startswith(("H_", "E_2del", "E_del")) for name in even)
    assert all(name.startswith("E_eps1_del") for name in odd)
    assert basis["ordering_convention"].startswith("PBW: [odd:")


@pytest.mark.parametrize("n", EXPECTED_DIMENSIONS)
def test_realizations_and_schema_consistency(n):
    basis = build_basis(n)
    realizations = build_realizations(n, basis)
    schema = build_schema(n, generation_date="2026-10-07")
    even, odd = basis["even"], basis["odd"]

    assert set(realizations) == set(even + odd)
    assert set(schema["generator_realization"]["realizations"]) == set(even + odd)
    assert schema["parity"] == {
        **{name: 0 for name in even},
        **{name: 1 for name in odd},
    }
    assert schema["algebra"]["dimension"] == {
        "total": EXPECTED_DIMENSIONS[n][2],
        "even": EXPECTED_DIMENSIONS[n][0],
        "odd": EXPECTED_DIMENSIONS[n][1],
    }
    assert schema["generator_realization"]["ordering"] == [
        "a_1_p",
        "a_1_m",
        *[
            f"b_{index}_{sign}"
            for index in range(1, n + 1)
            for sign in ("p", "m")
        ],
    ]
    assert schema["metadata"]["generation_date"] == "2026-10-07"
    assert "central_elements" in schema
    assert schema["central_elements"]["K"]["identity"] is True
    assert "K" not in schema["parity"]
    assert "kappa" not in schema["parity"]


@pytest.mark.parametrize("n", EXPECTED_DIMENSIONS)
def test_terminal_root_bracket_is_negative_terminal_cartan(n):
    basis = build_basis(n)
    realizations = build_realizations(n, basis)
    negative = f"E_2del{n}_m"
    positive = f"E_2del{n}_p"
    bracket = _bracket(
        realizations[negative]["polynomial"],
        realizations[positive]["polynomial"],
        0,
    )
    terminal_cartan = realizations[f"H_{n + 1}"]["polynomial"]

    assert {
        monomial: coeff
        for monomial, coeff in bracket.items()
        if coeff
    } == {
        monomial: -coeff
        for monomial, coeff in terminal_cartan.items()
        if coeff
    }


def test_fermion_and_boson_relations_are_normalized_exactly():
    zero = _word_polynomial([], 1)
    fermion_pair = _word_polynomial(["a_1_m", "a_1_p"], 1)
    expected_fermion = {key: Fraction(value) for key, value in zero.items()}
    expected_fermion.update(
        {
            key: expected_fermion.get(key, Fraction()) - coeff
            for key, coeff in _word_polynomial(["a_1_p", "a_1_m"], 1).items()
        }
    )
    assert fermion_pair == expected_fermion

    boson_pair = _word_polynomial(["b_1_m", "b_1_p"], 1)
    number_operator = _word_polynomial(["b_1_p", "b_1_m"], 1)
    expected_boson = dict(number_operator)
    for monomial, coeff in zero.items():
        expected_boson[monomial] = expected_boson.get(monomial, Fraction()) + coeff
    assert boson_pair == expected_boson


@pytest.mark.parametrize("n", EXPECTED_DIMENSIONS)
def test_structure_constants_are_nonzero_exact_graded_brackets(n):
    schema = build_schema(n, generation_date="2026-10-07")
    constants = schema["structure_constants"]
    parity = schema["parity"]

    assert constants
    assert all(entry["sign_rule"] == "graded" for entry in constants)
    assert all(Fraction(entry["coeff"]) for entry in constants)
    assert all(entry["Z"] in parity for entry in constants)

    coefficients = {
        (entry["X"], entry["Y"], entry["Z"]): Fraction(entry["coeff"])
        for entry in constants
    }
    for (left, right, result), coeff in coefficients.items():
        reverse = coefficients.get((right, left, result), Fraction())
        expected_reverse = -((-1) ** (parity[left] * parity[right])) * coeff
        assert reverse == expected_reverse

    assert coefficients[
        (f"E_2del{n}_m", f"E_2del{n}_p", f"H_{n + 1}")
    ] == -1


def test_fraction_format_is_exact():
    assert _fraction_string(Fraction(3, 1)) == "3"
    assert _fraction_string(Fraction(-1, 2)) == "-1/2"
