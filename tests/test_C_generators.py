from collections import defaultdict

import pytest
from sympy import Rational

from src.C_generators import (
    build_basis,
    build_realizations,
    build_schema,
    compute_structure_constants,
    normal_order_word,
)


@pytest.mark.parametrize(
    ("n", "even_count", "odd_count"),
    ((1, 4, 4), (2, 11, 8), (3, 22, 12)),
)
def test_basis_counts_and_parity(n, even_count, odd_count):
    even, odd, parity = build_basis(n)

    assert len(even) == even_count
    assert len(odd) == odd_count
    assert len(even) + len(odd) == 2 * n**2 + 5 * n + 1
    assert len(set(even + odd)) == len(even) + len(odd)
    assert set(parity) == set(even + odd)
    assert all(parity[label] == 0 for label in even)
    assert all(parity[label] == 1 for label in odd)


def test_basis_order_matches_approved_conventions():
    even, odd, _ = build_basis(2)

    assert even == [
        "H_1",
        "H_2",
        "H_3",
        "E_2del1_p",
        "E_2del2_p",
        "E_del1_del2_pp",
        "E_2del1_m",
        "E_2del2_m",
        "E_del1_del2_mm",
        "E_del1_del2_pm",
        "E_del1_del2_mp",
    ]
    assert odd == [
        "E_eps1_del1_pp",
        "E_eps1_del1_pm",
        "E_eps1_del2_pp",
        "E_eps1_del2_pm",
        "E_eps1_del1_mp",
        "E_eps1_del1_mm",
        "E_eps1_del2_mp",
        "E_eps1_del2_mm",
    ]


def test_normal_order_applies_car_and_ccr():
    assert normal_order_word(("a_1_p", "a_1_p")) == {}
    assert normal_order_word(("a_1_m", "a_1_p")) == {
        (): Rational(1),
        ("a_1_p", "a_1_m"): Rational(-1),
    }
    assert normal_order_word(("b_1_m", "b_1_p")) == {
        (): Rational(1),
        ("b_1_p", "b_1_m"): Rational(1),
    }
    assert normal_order_word(("b_1_m", "b_2_p")) == {
        ("b_2_p", "b_1_m"): Rational(1)
    }
    assert normal_order_word(("b_2_p", "a_1_p")) == {
        ("a_1_p", "b_2_p"): Rational(1)
    }


def test_realizations_use_approved_long_root_normalization():
    realizations = build_realizations(3)

    assert realizations["E_2del1_p"] == {
        ("b_1_p", "b_1_p"): Rational(1, 2)
    }
    assert realizations["E_2del3_m"] == {
        ("b_3_m", "b_3_m"): Rational(1, 2)
    }
    assert realizations["E_eps1_del2_mp"] == {
        ("a_1_m", "b_2_p"): Rational(1)
    }


@pytest.fixture(scope="module", params=(1, 2, 3))
def generated_algebra(request):
    n = request.param
    even, odd, parity = build_basis(n)
    constants = compute_structure_constants(n)
    bracket = defaultdict(dict)
    for entry in constants:
        bracket[(entry["X"], entry["Y"])][entry["Z"]] = Rational(entry["coeff"])
    return n, even, odd, parity, bracket


def _bracket(brackets, x, y):
    return brackets.get((x, y), {})


def _add_scaled(destination, source, scale):
    for label, coefficient in source.items():
        value = destination.get(label, Rational(0)) + scale * coefficient
        if value:
            destination[label] = value
        else:
            destination.pop(label, None)


def _nested_bracket(brackets, x, inner):
    result = {}
    for y, coefficient in inner.items():
        _add_scaled(result, _bracket(brackets, x, y), coefficient)
    return result


def test_structure_constants_are_closed_and_graded_skew(generated_algebra):
    _, even, odd, parity, brackets = generated_algebra
    labels = odd + even

    for x in labels:
        for y in labels:
            forward = _bracket(brackets, x, y)
            reverse = _bracket(brackets, y, x)
            sign = -1 if parity[x] * parity[y] else 1
            expected_reverse = {
                z: -sign * coefficient for z, coefficient in forward.items()
            }
            assert reverse == expected_reverse
            assert set(forward) <= set(labels)


def test_super_jacobi_identity(generated_algebra):
    _, even, odd, parity, brackets = generated_algebra
    labels = odd + even

    for x in labels:
        for y in labels:
            for z in labels:
                first = _nested_bracket(brackets, x, _bracket(brackets, y, z))
                second = _nested_bracket(brackets, y, _bracket(brackets, z, x))
                third = _nested_bracket(brackets, z, _bracket(brackets, x, y))
                result = {}
                _add_scaled(
                    result,
                    first,
                    Rational(-1 if parity[x] * parity[z] else 1),
                )
                _add_scaled(
                    result,
                    second,
                    Rational(-1 if parity[y] * parity[x] else 1),
                )
                _add_scaled(
                    result,
                    third,
                    Rational(-1 if parity[z] * parity[y] else 1),
                )
                assert result == {}, (x, y, z, result)


def test_in_memory_schema_matches_v5_conventions():
    schema = build_schema(1)

    assert schema["schema_version"] == "5.0"
    assert schema["algebra"]["family"] == "C"
    assert schema["algebra"]["m"] == 1
    assert schema["algebra"]["dimension"] == {
        "total": 8,
        "even": 4,
        "odd": 4,
    }
    assert set(schema["central_elements"]) == {"kappa", "K"}
    assert set(schema["parity"]) == set(
        schema["basis"]["even"] + schema["basis"]["odd"]
    )
    assert set(schema["generator_realization"]["realizations"]) == set(
        schema["parity"]
    )
    assert schema["structure_constants"]
