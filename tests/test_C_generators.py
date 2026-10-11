import json
from fractions import Fraction
from itertools import product
from pathlib import Path

import pytest

from src.C_generators import (
    build_basis,
    compute_bracket_table,
    generate_schema,
    normal_order_word,
    write_schema,
)


EXPECTED_DIMENSIONS = {
    1: (4, 4, 8),
    2: (11, 8, 19),
    3: (22, 12, 34),
}


@pytest.fixture(scope="module")
def computed_algebras():
    result = {}
    for n in EXPECTED_DIMENSIONS:
        basis = build_basis(n)
        constants, table = compute_bracket_table(basis)
        result[n] = basis, constants, table
    return result


@pytest.mark.parametrize("n", [1, 2, 3])
def test_basis_counts_labels_and_parity(n):
    basis = build_basis(n)
    expected_even, expected_odd, expected_total = EXPECTED_DIMENSIONS[n]

    assert len(basis.even) == expected_even
    assert len(basis.odd) == expected_odd
    assert len(basis.even) + len(basis.odd) == expected_total
    assert len(set(basis.even)) == len(basis.even)
    assert len(set(basis.odd)) == len(basis.odd)
    assert set(basis.even).isdisjoint(basis.odd)
    assert set(basis.parity) == set(basis.even) | set(basis.odd)
    assert all(basis.parity[label] == 0 for label in basis.even)
    assert all(basis.parity[label] == 1 for label in basis.odd)
    assert basis.even[:n + 1] == [f"H_{i}" for i in range(1, n + 2)]
    assert basis.odd == [
        f"E_eps1_del{k}_{suffix}"
        for k in range(1, n + 1)
        for suffix in ("pp", "pm", "mp", "mm")
    ]


def test_rank_one_exact_basis_order():
    basis = build_basis(1)
    assert basis.even == ["H_1", "H_2", "E_2del1_p", "E_2del1_m"]
    assert basis.odd == [
        "E_eps1_del1_pp",
        "E_eps1_del1_pm",
        "E_eps1_del1_mp",
        "E_eps1_del1_mm",
    ]


def test_normal_ordering_car_ccr_and_mixed_relations():
    assert normal_order_word(("a_1_m", "a_1_p")) == {
        (): Fraction(1),
        ("a_1_p", "a_1_m"): Fraction(-1),
    }
    assert normal_order_word(("a_1_p", "a_1_p")) == {}
    assert normal_order_word(("a_1_m", "a_1_m")) == {}
    assert normal_order_word(("b_1_m", "b_1_p")) == {
        (): Fraction(1),
        ("b_1_p", "b_1_m"): Fraction(1),
    }
    assert normal_order_word(("b_1_p", "b_2_p")) == {
        ("b_1_p", "b_2_p"): Fraction(1),
    }
    assert normal_order_word(("b_2_p", "b_1_p")) == {
        ("b_1_p", "b_2_p"): Fraction(1),
    }
    assert normal_order_word(("b_1_m", "a_1_p")) == {
        ("a_1_p", "b_1_m"): Fraction(1),
    }


@pytest.mark.parametrize("n", [1, 2, 3])
def test_realizations_cover_basis_and_match_parity(n):
    basis = build_basis(n)
    assert set(basis.realizations) == set(basis.even) | set(basis.odd)
    assert set(basis.polynomials) == set(basis.realizations)
    assert all(
        basis.realizations[label]["parity"] == basis.parity[label]
        for label in basis.realizations
    )
    assert all(
        basis.polynomials[label]
        for label in basis.realizations
    )


def _ordered_bracket(i, j, basis, table):
    if i <= j:
        return table[(i, j)]
    sign = -1 if basis.parity[basis.pbw_order[i]] * basis.parity[basis.pbw_order[j]] == 0 else 1
    return {label: sign * coefficient for label, coefficient in table[(j, i)].items()}


def _bracket_with_element(i, element, basis, table):
    result = {}
    for j, coefficient in element.items():
        for label, value in _ordered_bracket(i, j, basis, table).items():
            result[label] = result.get(label, Fraction()) + coefficient * value
            if not result[label]:
                del result[label]
    return result


@pytest.mark.parametrize("n", [1, 2, 3])
def test_every_bracket_closes_and_is_graded_skew(computed_algebras, n):
    basis, constants, table = computed_algebras[n]
    labels = basis.pbw_order
    assert len(table) == len(labels) * (len(labels) + 1) // 2
    assert constants

    for i in range(len(labels)):
        for j in range(len(labels)):
            forward = _ordered_bracket(i, j, basis, table)
            reverse = _ordered_bracket(j, i, basis, table)
            sign = -1 if basis.parity[labels[i]] * basis.parity[labels[j]] == 0 else 1
            assert forward == {
                label: sign * coefficient
                for label, coefficient in reverse.items()
            }


@pytest.mark.parametrize("n", [1, 2, 3])
def test_super_jacobi_identity(computed_algebras, n):
    basis, _, table = computed_algebras[n]
    labels = basis.pbw_order
    for i, j, k in product(range(len(labels)), repeat=3):
        pi, pj, pk = (basis.parity[labels[index]] for index in (i, j, k))
        terms = (
            ((-1) ** (pi * pk), i, _ordered_bracket(j, k, basis, table)),
            ((-1) ** (pj * pi), j, _ordered_bracket(k, i, basis, table)),
            ((-1) ** (pk * pj), k, _ordered_bracket(i, j, basis, table)),
        )
        jacobi = {}
        for scale, outer, inner in terms:
            for label, coefficient in _bracket_with_element(
                outer, inner, basis, table
            ).items():
                jacobi[label] = jacobi.get(label, Fraction()) + scale * coefficient
                if not jacobi[label]:
                    del jacobi[label]
        assert jacobi == {}


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema_fields_constants_and_deterministic_serialization(
    computed_algebras, n
):
    basis, constants, _ = computed_algebras[n]
    schema = generate_schema(n, generation_date="2026-10-11")
    labels = set(basis.even) | set(basis.odd)

    assert set(schema) == {
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
    assert schema["schema_version"] == "5.0"
    assert schema["algebra"]["m"] == 1
    assert schema["algebra"]["n"] == n
    assert schema["algebra"]["dimension"]["even"] == EXPECTED_DIMENSIONS[n][0]
    assert schema["algebra"]["dimension"]["odd"] == EXPECTED_DIMENSIONS[n][1]
    assert schema["algebra"]["dimension"]["total"] == EXPECTED_DIMENSIONS[n][2]
    assert schema["basis"]["even"] == basis.even
    assert schema["basis"]["odd"] == basis.odd
    assert set(schema["parity"]) == labels
    assert set(schema["generator_realization"]["realizations"]) == labels
    assert schema["oscillator_generators"]["fermions"]["labels"] == [
        "a_1_p", "a_1_m"
    ]
    assert schema["oscillator_generators"]["fermions"]["m"] == 1
    assert schema["oscillator_generators"]["bosons"]["n"] == n
    assert schema["oscillator_generators"]["bosons"]["count"] == 2 * n
    assert schema["central_elements"]["kappa"]["parity"] == 1
    assert schema["central_elements"]["K"]["parity"] == 0
    assert "standard_fermion_anticommutators" in schema["oscillator_relations"]
    assert schema["metadata"]["generated_by"] == "C_generators.py"
    assert schema["structure_constants"] == constants
    assert all(set(record) == {"X", "Y", "Z", "coeff", "sign_rule"}
               for record in constants)
    order_index = {label: index for index, label in enumerate(basis.pbw_order)}
    assert all(
        record["X"] in labels
        and record["Y"] in labels
        and record["Z"] in labels
        and order_index[record["X"]] <= order_index[record["Y"]]
        and record["sign_rule"] == "graded"
        and Fraction(record["coeff"]) != 0
        for record in constants
    )
    assert constants == sorted(
        constants,
        key=lambda record: (
            order_index[record["X"]],
            order_index[record["Y"]],
            order_index[record["Z"]],
        ),
    )
    serialized = json.dumps(schema, ensure_ascii=False, indent=2) + "\n"
    assert serialized == json.dumps(
        generate_schema(n, generation_date="2026-10-11"),
        ensure_ascii=False,
        indent=2,
    ) + "\n"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_write_schema_uses_rank_filename_and_valid_json(tmp_path, n):
    output_path = write_schema(n, tmp_path, generation_date="2026-10-11")
    assert output_path == Path(tmp_path) / f"C_{n}_structure.json"
    generated = json.loads(output_path.read_text(encoding="utf-8"))
    assert generated["algebra"]["n"] == n


@pytest.mark.parametrize("n", [1, 2, 3])
def test_checked_in_data_matches_generator(n):
    data_path = Path(__file__).resolve().parents[1] / "data" / f"C_{n}_structure.json"
    generated = json.loads(data_path.read_text(encoding="utf-8"))
    regenerated = generate_schema(
        n,
        generation_date=generated["metadata"]["generation_date"],
    )
    assert generated == regenerated
