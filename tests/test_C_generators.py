from __future__ import annotations

from fractions import Fraction

import pytest

from src.C_generators import build_schema


@pytest.mark.parametrize(
    ("rank", "even_count", "odd_count"),
    ((1, 4, 4), (2, 11, 8), (3, 22, 12)),
)
def test_schema_basis_dimensions_and_parity(
    rank: int, even_count: int, odd_count: int
) -> None:
    schema = build_schema(rank)
    basis = schema["basis"]
    parity = schema["parity"]

    assert len(basis["even"]) == even_count
    assert len(basis["odd"]) == odd_count
    assert schema["algebra"]["dimension"] == {
        "total": even_count + odd_count,
        "even": even_count,
        "odd": odd_count,
        "even_formula": "2n^2 + n + 1",
        "odd_formula": "4n",
        "total_formula": "2n^2 + 5n + 1",
    }
    assert set(parity) == set(basis["even"]) | set(basis["odd"])
    assert all(parity[label] == 0 for label in basis["even"])
    assert all(parity[label] == 1 for label in basis["odd"])
    assert set(schema["generator_realization"]["realizations"]) == set(parity)
    assert len(schema["structure_constants"]) > 0


@pytest.mark.parametrize("rank", (1, 2, 3))
def test_structure_constants_are_valid_and_canonical(rank: int) -> None:
    schema = build_schema(rank)
    basis = list(schema["generator_realization"]["realizations"])
    basis_order = {label: index for index, label in enumerate(basis)}
    parity = schema["parity"]

    for entry in schema["structure_constants"]:
        assert entry["X"] in basis_order
        assert entry["Y"] in basis_order
        assert entry["Z"] in basis_order
        assert basis_order[entry["X"]] <= basis_order[entry["Y"]]
        assert entry["sign_rule"] == "graded"
        assert Fraction(entry["coeff"])
        assert parity[entry["Z"]] == (parity[entry["X"]] + parity[entry["Y"]]) % 2


@pytest.mark.parametrize("rank", (1, 2, 3))
def test_structure_constants_satisfy_super_jacobi(rank: int) -> None:
    schema = build_schema(rank)
    basis = list(schema["generator_realization"]["realizations"])
    parity = schema["parity"]
    bracket_table: dict[tuple[str, str], dict[str, Fraction]] = {}
    for entry in schema["structure_constants"]:
        key = entry["X"], entry["Y"]
        bracket_table.setdefault(key, {})[entry["Z"]] = Fraction(entry["coeff"])

    def bracket(left: str, right: str) -> dict[str, Fraction]:
        if basis.index(left) <= basis.index(right):
            return bracket_table.get((left, right), {})
        sign = -1 if (parity[left] * parity[right]) % 2 == 0 else 1
        return {
            label: sign * coefficient
            for label, coefficient in bracket_table.get((right, left), {}).items()
        }

    def nested(left: str, right: str, third: str) -> dict[str, Fraction]:
        result: dict[str, Fraction] = {}
        for middle, coefficient in bracket(right, third).items():
            for output, nested_coefficient in bracket(left, middle).items():
                result[output] = result.get(output, Fraction(0)) + (
                    coefficient * nested_coefficient
                )
                if not result[output]:
                    del result[output]
        return result

    for x in basis:
        for y in basis:
            for z in basis:
                terms = (
                    (nested(x, y, z), (-1) ** (parity[x] * parity[z])),
                    (nested(y, z, x), (-1) ** (parity[y] * parity[x])),
                    (nested(z, x, y), (-1) ** (parity[z] * parity[y])),
                )
                total: dict[str, Fraction] = {}
                for term, sign in terms:
                    for label, coefficient in term.items():
                        total[label] = total.get(label, Fraction(0)) + sign * coefficient
                        if not total[label]:
                            del total[label]
                assert not total, (x, y, z, total)


def test_oscillator_labels_and_central_elements() -> None:
    schema = build_schema(2)
    assert schema["oscillator_generators"]["fermions"]["labels"] == [
        "a_1_p",
        "a_1_m",
    ]
    assert schema["oscillator_generators"]["bosons"]["labels"] == [
        "b_1_p",
        "b_1_m",
        "b_2_p",
        "b_2_m",
    ]
    assert schema["central_elements"]["kappa"]["parity"] == 1
    assert schema["central_elements"]["K"]["parity"] == 0
    assert "supplementary_fermion" not in schema["oscillator_generators"]


def test_fermionic_and_bosonic_generators_have_expected_realizations() -> None:
    schema = build_schema(2)
    realizations = schema["generator_realization"]["realizations"]
    assert realizations["E_eps1_del2_mp"]["frappat_form"] == "a_1^- b_2^+"
    assert realizations["E_del1_del2_pm"]["frappat_form"] == "b_1^+ b_2^-"


def test_rank_must_be_positive() -> None:
    with pytest.raises(ValueError, match="at least 1"):
        build_schema(0)
