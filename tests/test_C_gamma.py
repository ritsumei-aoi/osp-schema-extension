import json
import re
from fractions import Fraction
from pathlib import Path

import pytest

from src.C_gamma import (
    deformed_bracket,
    generate_gamma_schema,
    normal_order_deformed_word,
)
from src.C_generators import build_basis


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def _parse_linear_coefficient(expression):
    terms = {}
    parts = re.split(r" ([+-]) ", expression)
    for index in range(0, len(parts), 2):
        sign = 1 if index == 0 or parts[index - 1] == "+" else -1
        term = parts[index]
        if index == 0 and term.startswith("-"):
            sign *= -1
            term = term[1:]
        if "*" in term:
            scalar, parameter = term.split("*", maxsplit=1)
            coefficient = Fraction(scalar)
        else:
            coefficient, parameter = Fraction(1), term
        terms[parameter] = terms.get(parameter, Fraction()) + sign * coefficient
    return {parameter: coefficient for parameter, coefficient in terms.items() if coefficient}


def _gamma_records_by_key(schema):
    records = schema["inhomogeneous_deformation"]["gamma_structure"]
    by_key = {}
    for record in records:
        key = (record["X"], record["Y"], record["Z"])
        assert key not in by_key
        by_key[key] = _parse_linear_coefficient(record["coeff"])
    return by_key


def test_deformed_normal_ordering_uses_literal_relation_and_kappa_parity():
    direct = normal_order_deformed_word(("b_1_p", "a_1_p"))
    assert direct.base == {("a_1_p", "b_1_p"): Fraction(1)}
    assert direct.corrections == {"gb_a1_p_b1_p": {(): Fraction(-1)}}

    with_odd_prefix = normal_order_deformed_word(
        ("a_1_p", "b_1_p", "a_1_m")
    )
    assert with_odd_prefix.base == {
        ("a_1_p", "a_1_m", "b_1_p"): Fraction(1),
    }
    assert with_odd_prefix.corrections == {
        "gb_a1_m_b1_p": {("a_1_p",): Fraction(1)},
    }


def test_deformed_bracket_keeps_schema1_bracket_and_first_order_corrections():
    basis = build_basis(1)
    odd_root = basis.polynomials["E_eps1_del1_pp"]
    cartan = basis.polynomials["H_1"]
    result = deformed_bracket(odd_root, cartan, 1, 0)

    assert result.base
    assert result.corrections
    assert result.corrections["gb_a1_p_b1_p"] == {
        ("a_1_p", "a_1_m"): Fraction(1),
        ("b_1_p", "b_1_m"): Fraction(1),
        (): Fraction(1),
    }


@pytest.mark.parametrize("n", [1, 2, 3])
def test_gamma_schema_matches_matrix_and_contains_expected_central_terms(n):
    schema1 = json.loads((DATA_DIR / f"C_{n}_structure.json").read_text())
    gamma = generate_gamma_schema(schema1, generation_date="2026-10-11")
    matrix = gamma["gb_matrix"]
    deformation = gamma["inhomogeneous_deformation"]

    assert matrix["shape"] == [2, 2 * n]
    assert matrix["parity"] == 0
    assert matrix["row_labels"] == ["a_1_p", "a_1_m"]
    assert matrix["column_labels"] == [
        label
        for index in range(1, n + 1)
        for label in (f"b_{index}_p", f"b_{index}_m")
    ]
    assert len(matrix["parameters"]) == 2
    assert all(len(row) == 2 * n for row in matrix["parameters"])
    assert deformation["kappa_parity"] == 1
    assert deformation["deformation_term_parity"] == 1
    assert any(record["Z"] == "K" for record in deformation["gamma_structure"])
    assert gamma["metadata"]["schema1_file"] == f"C_{n}_structure.json"
    assert gamma == json.loads(
        (DATA_DIR / f"C_{n}_gamma.json").read_text(encoding="utf-8")
    )


@pytest.mark.parametrize("n", [1, 2, 3])
def test_gamma_records_are_nonzero_parity_homogeneous_and_graded_skew(n):
    gamma = json.loads((DATA_DIR / f"C_{n}_gamma.json").read_text())
    basis = build_basis(n)
    parity = {**basis.parity, "K": 0}
    records = _gamma_records_by_key(gamma)
    labels = set(basis.pbw_order)

    assert records
    for (x, y, z), coefficients in records.items():
        assert x in labels and y in labels
        assert z in labels | {"K"}
        assert coefficients
        assert parity[z] == (parity[x] + parity[y] + 1) % 2

    for x in basis.pbw_order:
        for y in basis.pbw_order:
            factor = -1 if basis.parity[x] * basis.parity[y] == 0 else 1
            for z in labels | {"K"}:
                assert records.get((x, y, z), {}) == {
                    parameter: factor * coefficient
                    for parameter, coefficient in records.get((y, x, z), {}).items()
                }
