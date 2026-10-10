from fractions import Fraction

import pytest

from src.C_generators import (
    _bracket,
    _make_basis,
    build_schema,
    normal_order_word,
)


@pytest.mark.parametrize(
    ("n", "even_count", "odd_count", "total"),
    [(1, 4, 4, 8), (2, 11, 8, 19), (3, 22, 12, 34)],
)
def test_basis_counts_and_parity(n, even_count, odd_count, total):
    schema = build_schema(n)

    assert len(schema["basis"]["even"]) == even_count
    assert len(schema["basis"]["odd"]) == odd_count
    assert schema["algebra"]["dimension"]["total"] == total
    assert len(schema["parity"]) == total
    assert all(schema["parity"][label] == 0 for label in schema["basis"]["even"])
    assert all(schema["parity"][label] == 1 for label in schema["basis"]["odd"])
    assert "supplementary_fermion" not in schema["oscillator_generators"]
    assert schema["oscillator_generators"]["fermions"]["labels"] == [
        "a_1_p",
        "a_1_m",
    ]


@pytest.mark.parametrize("n", [1, 2, 3])
def test_basis_uses_approved_root_triangular_order(n):
    labels, parity, _ = _make_basis(n)

    negative_odd = [
        label for label in labels if label.startswith("E_eps1_") and label.endswith(("mm", "mp"))
    ]
    cartan = [label for label in labels if label.startswith("H_")]
    first_cartan = labels.index(cartan[0])
    last_cartan = labels.index(cartan[-1])

    assert labels[: len(negative_odd)] == negative_odd
    assert labels[first_cartan : last_cartan + 1] == cartan
    assert all(parity[label] == 1 for label in negative_odd)
    assert labels.index("H_1") < labels.index("E_2del1_p")


def test_oscillator_relations_are_applied_exactly():
    n = 2
    assert normal_order_word(("a_1_m", "a_1_p"), n) == {
        (): Fraction(1),
        ("a_1_p", "a_1_m"): Fraction(-1),
    }
    assert normal_order_word(("b_1_m", "b_1_p"), n) == {
        (): Fraction(1),
        ("b_1_p", "b_1_m"): Fraction(1),
    }
    assert normal_order_word(("a_1_p", "a_1_p"), n) == {}
    assert normal_order_word(("b_2_p", "b_1_m"), n) == {
        ("b_1_m", "b_2_p"): Fraction(1)
    }


def test_long_root_realizations_use_half_normalization():
    schema = build_schema(2)
    realizations = schema["generator_realization"]["realizations"]

    for k in (1, 2):
        for sign in ("p", "m"):
            entry = realizations[f"E_2del{k}_{sign}"]
            assert entry["standard_form"] == [
                {"words": [f"b_{k}_{sign}", f"b_{k}_{sign}"], "coeff": "1/2"}
            ]


@pytest.mark.parametrize("n", [1, 2, 3])
def test_structure_constants_are_nonzero_and_reference_basis(n):
    schema = build_schema(n)
    basis = set(schema["basis"]["even"] + schema["basis"]["odd"])

    assert schema["structure_constants"]
    assert all(item["X"] in basis for item in schema["structure_constants"])
    assert all(item["Y"] in basis for item in schema["structure_constants"])
    assert all(item["Z"] in basis for item in schema["structure_constants"])
    assert all(item["coeff"] not in ("0", "0/1") for item in schema["structure_constants"])
    assert all(item["sign_rule"] == "graded" for item in schema["structure_constants"])


@pytest.mark.parametrize("n", [1, 2, 3])
def test_structure_constants_include_both_bracket_orderings(n):
    schema = build_schema(n)
    parity = schema["parity"]
    coefficients = {
        (item["X"], item["Y"], item["Z"]): Fraction(item["coeff"])
        for item in schema["structure_constants"]
    }

    for (left, right, result), coefficient in coefficients.items():
        sign = -1 if parity[left] * parity[right] % 2 else 1
        assert coefficients[(right, left, result)] == -sign * coefficient


def test_superbracket_sign_and_closure_for_rank_one():
    labels, parity, generators = _make_basis(1)
    odd = "E_eps1_del1_pp"
    cartan = "H_2"

    bracket = _bracket(generators[cartan], generators[odd], parity[cartan], parity[odd], 1)
    assert bracket == {("a_1_p", "b_1_p"): Fraction(-1)}
    assert labels.index("H_2") < labels.index("E_eps1_del1_pp")


def test_schema_has_required_top_level_fields_and_central_elements():
    schema = build_schema(1, generation_date="2026-01-01")

    assert schema["schema_version"] == "5.0"
    assert schema["algebra"]["family"] == "C"
    assert schema["algebra"]["m"] == 1
    assert schema["central_elements"]["kappa"]["parity"] == 1
    assert schema["central_elements"]["K"]["parity"] == 0
    assert schema["metadata"]["generation_date"] == "2026-01-01"
    assert "a_0" not in schema["generator_realization"]["ordering"]


@pytest.mark.parametrize("n", [1, 2, 3])
def test_super_jacobi_identity_for_all_basis_triples(n):
    schema = build_schema(n)
    labels, parity, _ = _make_basis(n)
    indices = {label: index for index, label in enumerate(labels)}
    bracket_table = {}
    for item in schema["structure_constants"]:
        key = (indices[item["X"]], indices[item["Y"]])
        bracket_table.setdefault(key, {})[indices[item["Z"]]] = Fraction(item["coeff"])

    def basis_bracket(left, right):
        return bracket_table.get((left, right), {})

    def vector_bracket(left, right):
        result = {}
        for left_index, left_coefficient in left.items():
            for right_index, right_coefficient in right.items():
                for index, coefficient in basis_bracket(
                    left_index, right_index
                ).items():
                    result[index] = (
                        result.get(index, Fraction(0))
                        + left_coefficient * right_coefficient * coefficient
                    )
        return {index: value for index, value in result.items() if value}

    def scaled(vector, factor):
        return {
            index: coefficient * factor
            for index, coefficient in vector.items()
            if coefficient * factor
        }

    for x in range(len(labels)):
        for y in range(len(labels)):
            for z in range(len(labels)):
                px, py, pz = (parity[labels[index]] for index in (x, y, z))
                first = scaled(
                    vector_bracket(
                        {x: Fraction(1)},
                        vector_bracket({y: Fraction(1)}, {z: Fraction(1)}),
                    ),
                    -1 if px * pz % 2 else 1,
                )
                second = scaled(
                    vector_bracket(
                        {y: Fraction(1)},
                        vector_bracket({z: Fraction(1)}, {x: Fraction(1)}),
                    ),
                    -1 if py * px % 2 else 1,
                )
                third = scaled(
                    vector_bracket(
                        {z: Fraction(1)},
                        vector_bracket({x: Fraction(1)}, {y: Fraction(1)}),
                    ),
                    -1 if pz * py % 2 else 1,
                )
                assert not {
                    index: first.get(index, Fraction(0))
                    + second.get(index, Fraction(0))
                    + third.get(index, Fraction(0))
                    for index in first.keys() | second.keys() | third.keys()
                    if first.get(index, Fraction(0))
                    + second.get(index, Fraction(0))
                    + third.get(index, Fraction(0))
                }, f"super-Jacobi failed for ({labels[x]}, {labels[y]}, {labels[z]})"
