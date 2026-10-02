"""Compute first-order inhomogeneous gamma data for C(n+1)."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Any, TypeAlias

from sympy import Matrix, Poly, Rational, Symbol, expand

if __package__:
    from .C_generators import (
        FERMION_MINUS,
        FERMION_PLUS,
        Polynomial,
        Word,
        _oscillator_key,
        build_basis,
        build_realizations,
        graded_bracket,
        normal_order_word,
    )
else:
    from C_generators import (
        FERMION_MINUS,
        FERMION_PLUS,
        Polynomial,
        Word,
        _oscillator_key,
        build_basis,
        build_realizations,
        graded_bracket,
        normal_order_word,
    )

DeformedKey: TypeAlias = tuple[Word, bool]
DeformedPolynomial: TypeAlias = dict[DeformedKey, Any]
_BOSON_PATTERN = re.compile(r"^b_(\d+)_(p|m)$")


def _add_term(
    polynomial: DeformedPolynomial,
    key: DeformedKey,
    coefficient: Any,
) -> None:
    value = expand(polynomial.get(key, 0) + coefficient)
    if value:
        polynomial[key] = value
    else:
        polynomial.pop(key, None)


def _combine(
    destination: DeformedPolynomial,
    source: DeformedPolynomial,
    scale: Any = Rational(1),
) -> None:
    for key, coefficient in source.items():
        _add_term(destination, key, scale * coefficient)


def _parameter_for_pair(boson: str, fermion: str) -> Symbol:
    match = _BOSON_PATTERN.fullmatch(boson)
    if match is None or fermion not in (FERMION_PLUS, FERMION_MINUS):
        raise ValueError(f"Invalid mixed oscillator pair: {boson}, {fermion}")
    index, boson_sign = match.groups()
    fermion_sign = "p" if fermion == FERMION_PLUS else "m"
    return Symbol(f"gb_a1_{fermion_sign}_b{index}_{boson_sign}")


@lru_cache(maxsize=None)
def _deformed_normal_order_word(word: Word) -> tuple[tuple[DeformedKey, Any], ...]:
    """Normal-order an undeformed word, retaining first-order gb*kappa terms."""
    for index in range(len(word) - 1):
        left, right = word[index], word[index + 1]
        prefix, suffix = word[:index], word[index + 2 :]

        if left in (FERMION_PLUS, FERMION_MINUS) and right in (
            FERMION_PLUS,
            FERMION_MINUS,
        ):
            if left == right:
                return ()
            if left == FERMION_MINUS and right == FERMION_PLUS:
                result: DeformedPolynomial = {}
                _combine(
                    result,
                    dict(_deformed_normal_order_word(prefix + suffix)),
                )
                _combine(
                    result,
                    dict(
                        _deformed_normal_order_word(
                            prefix + (FERMION_PLUS, FERMION_MINUS) + suffix
                        )
                    ),
                    Rational(-1),
                )
                return tuple(
                    sorted(result.items(), key=lambda item: _deformed_key_sort(item[0]))
                )

        left_match = _BOSON_PATTERN.fullmatch(left)
        right_match = _BOSON_PATTERN.fullmatch(right)
        if left_match and right_match:
            left_index, left_sign = left_match.groups()
            right_index, right_sign = right_match.groups()
            if left_sign == "m" and right_sign == "p":
                result = {}
                if left_index == right_index:
                    _combine(result, dict(_deformed_normal_order_word(prefix + suffix)))
                _combine(
                    result,
                    dict(_deformed_normal_order_word(prefix + (right, left) + suffix)),
                )
                return tuple(
                    sorted(result.items(), key=lambda item: _deformed_key_sort(item[0]))
                )

        if left.startswith("b_") and right in (FERMION_PLUS, FERMION_MINUS):
            result = {}
            _combine(
                result,
                dict(_deformed_normal_order_word(prefix + (right, left) + suffix)),
            )

            prefix_parity = sum(
                letter in (FERMION_PLUS, FERMION_MINUS) for letter in prefix
            ) % 2
            correction = -_parameter_for_pair(left, right)
            if prefix_parity:
                correction = -correction
            for normalized_word, coefficient in normal_order_word(prefix + suffix).items():
                _add_term(
                    result,
                    ((normalized_word), True),
                    correction * coefficient,
                )
            return tuple(
                sorted(result.items(), key=lambda item: _deformed_key_sort(item[0]))
            )

        if _oscillator_key(left) > _oscillator_key(right):
            reordered = word[:index] + (right, left) + word[index + 2 :]
            return _deformed_normal_order_word(reordered)

    return (((word, False), Rational(1)),)


def _deformed_key_sort(key: DeformedKey) -> tuple[tuple[tuple[int, ...], ...], bool]:
    return tuple(_oscillator_key(letter) for letter in key[0]), key[1]


def _multiply_deformed(
    left: DeformedPolynomial,
    right: DeformedPolynomial,
) -> DeformedPolynomial:
    result: DeformedPolynomial = {}
    for (left_word, left_kappa), left_coefficient in left.items():
        for (right_word, right_kappa), right_coefficient in right.items():
            if left_kappa and right_kappa:
                continue
            coefficient = left_coefficient * right_coefficient
            if right_kappa and not left_kappa:
                if sum(
                    letter in (FERMION_PLUS, FERMION_MINUS)
                    for letter in left_word
                ) % 2:
                    coefficient = -coefficient

            if left_kappa or right_kappa:
                for word, factor in normal_order_word(left_word + right_word).items():
                    _add_term(result, (word, True), coefficient * factor)
            else:
                for key, factor in _deformed_normal_order_word(left_word + right_word):
                    _add_term(result, key, coefficient * factor)
    return result


def _graded_bracket_deformed(
    left: DeformedPolynomial,
    right: DeformedPolynomial,
    left_parity: int,
    right_parity: int,
) -> DeformedPolynomial:
    sign = -1 if left_parity * right_parity else 1
    result = _multiply_deformed(left, right)
    _combine(result, _multiply_deformed(right, left), Rational(-sign))
    return result


def _coordinate_solver(
    labels: list[str],
    realizations: dict[str, Polynomial],
    modulo_scalar: bool = False,
) -> tuple[list[Word], Matrix, list[int], Matrix]:
    monomials = sorted(
        {
            word
            for polynomial in realizations.values()
            for word in polynomial
            if not modulo_scalar or word != ()
        },
        key=lambda word: tuple(_oscillator_key(letter) for letter in word),
    )
    matrix = Matrix(
        [
            [realizations[label].get(word, Rational(0)) for label in labels]
            for word in monomials
        ]
    )
    if matrix.rank() != len(labels):
        raise ValueError("Schema 1 generator realizations are linearly dependent")
    _, pivot_columns = matrix.T.rref()
    pivot_rows = list(pivot_columns)
    inverse = matrix.extract(pivot_rows, list(range(len(labels)))).inv()
    return monomials, matrix, pivot_rows, inverse


def _project_to_basis(
    polynomial: Polynomial,
    labels: list[str],
    monomials: list[Word],
    matrix: Matrix,
    pivot_rows: list[int],
    inverse: Matrix,
) -> dict[str, Rational]:
    unknown = set(polynomial) - set(monomials)
    if unknown:
        raise ValueError(f"Gamma contains monomials outside the Schema 1 span: {unknown}")
    vector = Matrix([polynomial.get(word, Rational(0)) for word in monomials])
    coordinates = inverse * Matrix([vector[row] for row in pivot_rows])
    residual = vector - matrix * coordinates
    if residual != Matrix.zeros(len(monomials), 1):
        terms = {
            monomials[index]: residual[index]
            for index in range(len(monomials))
            if residual[index]
        }
        raise ValueError(f"Gamma output is not in the Schema 1 generator span: {terms}")
    return {
        label: Rational(coordinates[index])
        for index, label in enumerate(labels)
        if coordinates[index]
    }


def _parameter_symbols(n: int) -> list[Symbol]:
    return [
        _parameter_for_pair(f"b_{index}_{boson_sign}", fermion)
        for fermion in (FERMION_PLUS, FERMION_MINUS)
        for index in range(1, n + 1)
        for boson_sign in ("p", "m")
    ]


def _extract_parameter_polynomials(
    deformed_bracket: DeformedPolynomial,
    parameters: list[Symbol],
) -> dict[Symbol, Polynomial]:
    by_parameter: dict[Symbol, Polynomial] = {parameter: {} for parameter in parameters}
    for (word, has_kappa), expression in deformed_bracket.items():
        if not has_kappa:
            continue
        expanded = expand(expression)
        if not expanded:
            continue
        expression_poly = Poly(expanded, *parameters)
        if expression_poly.total_degree() > 1 or expression_poly.coeff_monomial(1):
            raise ValueError("Gamma correction is not homogeneous and linear in gb")
        for monomial, coefficient in expression_poly.terms():
            if sum(monomial) != 1:
                raise ValueError("Gamma correction contains a nonlinear gb term")
            parameter_index = monomial.index(1)
            parameter = parameters[parameter_index]
            rational = Rational(coefficient)
            by_parameter[parameter][word] = (
                by_parameter[parameter].get(word, Rational(0)) + rational
            )
    return {
        parameter: polynomial
        for parameter, polynomial in by_parameter.items()
        if polynomial
    }


def _format_gamma_coefficient(terms: dict[Symbol, Rational]) -> str:
    pieces: list[str] = []
    for parameter in sorted(terms, key=str):
        coefficient = terms[parameter]
        magnitude = abs(coefficient)
        if magnitude == 1:
            body = str(parameter)
        else:
            body = f"{magnitude}*{parameter}"
        if not pieces:
            pieces.append(f"-{body}" if coefficient < 0 else body)
        else:
            pieces.append(f" - {body}" if coefficient < 0 else f" + {body}")
    return "".join(pieces)


def _schema1_brackets(schema1: dict[str, Any]) -> dict[tuple[str, str], dict[str, Rational]]:
    brackets: dict[tuple[str, str], dict[str, Rational]] = defaultdict(dict)
    for record in schema1["structure_constants"]:
        brackets[(record["X"], record["Y"])][record["Z"]] = Rational(record["coeff"])
    return brackets


def compute_gamma_schema(
    n: int,
    schema1: dict[str, Any],
) -> dict[str, Any]:
    """Compute all first-order gamma coefficients against one Schema 1 basis."""
    even, odd, parity = build_basis(n)
    labels = odd + even
    if schema1["algebra"]["n"] != n:
        raise ValueError("Schema 1 rank does not match requested gamma rank")
    if schema1["basis"]["even"] != even or schema1["basis"]["odd"] != odd:
        raise ValueError("Schema 1 basis differs from the approved C(n+1) basis")
    schema1_brackets = _schema1_brackets(schema1)
    realizations = build_realizations(n)
    monomials, matrix, pivot_rows, inverse = _coordinate_solver(labels, realizations)
    quotient_monomials, quotient_matrix, quotient_pivots, quotient_inverse = (
        _coordinate_solver(labels, realizations, modulo_scalar=True)
    )
    parameters = _parameter_symbols(n)

    gamma_terms: dict[tuple[str, str, str], dict[Symbol, Rational]] = {}
    scalar_components_discarded = 0
    for x in labels:
        for y in labels:
            base_x = {(word, False): coefficient for word, coefficient in realizations[x].items()}
            base_y = {(word, False): coefficient for word, coefficient in realizations[y].items()}
            deformed_bracket = _graded_bracket_deformed(
                base_x, base_y, parity[x], parity[y]
            )

            undeformed = {
                word: coefficient
                for (word, has_kappa), coefficient in deformed_bracket.items()
                if not has_kappa
            }
            expected_undeformed = graded_bracket(
                realizations[x], realizations[y], parity[x], parity[y]
            )
            if undeformed != expected_undeformed:
                raise ValueError(f"Undeformed bracket mismatch for ({x}, {y})")
            expected_coordinates = _project_to_basis(
                expected_undeformed, labels, monomials, matrix, pivot_rows, inverse
            )
            if expected_coordinates != schema1_brackets.get((x, y), {}):
                raise ValueError(f"Schema 1 constants mismatch for ({x}, {y})")

            parameter_polynomials = _extract_parameter_polynomials(
                deformed_bracket, parameters
            )
            by_output: dict[str, dict[Symbol, Rational]] = defaultdict(dict)
            for parameter, polynomial in parameter_polynomials.items():
                quotient_polynomial = {
                    word: coefficient
                    for word, coefficient in polynomial.items()
                    if word != ()
                }
                coordinates = _project_to_basis(
                    quotient_polynomial,
                    labels,
                    quotient_monomials,
                    quotient_matrix,
                    quotient_pivots,
                    quotient_inverse,
                )
                scalar_residual = polynomial.get((), Rational(0)) - sum(
                    coefficient * realizations[z].get((), Rational(0))
                    for z, coefficient in coordinates.items()
                )
                scalar_components_discarded += bool(scalar_residual)
                for z, coefficient in coordinates.items():
                    if parity[z] != (parity[x] + parity[y] + 1) % 2:
                        raise ValueError(
                            f"Gamma parity mismatch for ({x}, {y}) -> {z}"
                        )
                    by_output[z][parameter] = coefficient
            for z, coefficients in by_output.items():
                gamma_terms[(x, y, z)] = coefficients

    for x in labels:
        for y in labels:
            sign = -1 if parity[x] * parity[y] else 1
            for z in labels:
                forward = gamma_terms.get((x, y, z), {})
                reverse = gamma_terms.get((y, x, z), {})
                expected = {
                    parameter: -sign * coefficient
                    for parameter, coefficient in reverse.items()
                }
                if forward != expected:
                    raise ValueError(
                        f"Gamma graded anti-symmetry mismatch for ({x}, {y}) -> {z}"
                    )

    gamma_structure = [
        {
            "X": x,
            "Y": y,
            "Z": z,
            "coeff": _format_gamma_coefficient(gamma_terms[(x, y, z)]),
            "sign_rule": "graded",
        }
        for x in labels
        for y in labels
        for z in labels
        if (x, y, z) in gamma_terms
    ]

    row_labels = [FERMION_PLUS, FERMION_MINUS]
    column_labels = [
        label
        for index in range(1, n + 1)
        for label in (f"b_{index}_p", f"b_{index}_m")
    ]
    parameter_names = {
        (fermion, boson): str(_parameter_for_pair(boson, fermion))
        for fermion in row_labels
        for boson in column_labels
    }
    gb_matrix = {
        "row_labels": row_labels,
        "column_labels": column_labels,
        "entries": [
            [parameter_names[(fermion, boson)] for boson in column_labels]
            for fermion in row_labels
        ],
        "parameter_parity": 0,
    }
    deformed_relations = [
        {
            "X": boson,
            "Y": fermion,
            "parameter": parameter_names[(fermion, boson)],
            "coefficient": "-1",
            "central_element": "κ",
            "relation": f"[{boson}, {fermion}]_γ - [{boson}, {fermion}]_0 = "
            f"-{parameter_names[(fermion, boson)]} * κ",
        }
        for fermion in row_labels
        for boson in column_labels
    ]

    return {
        "schema_version": "5.0",
        "algebra": schema1["algebra"],
        "inhomogeneous_deformation": {
            "gb_matrix": gb_matrix,
            "deformed_relations": deformed_relations,
            "gamma_structure": gamma_structure,
            "scalar_projection": {
                "central_element": "K",
                "policy": "project modulo scalar K and discard the residual scalar component",
                "discarded_parameter_components": scalar_components_discarded,
            },
        },
        "metadata": {
            "generated_by": "build_C_gamma_schema.py",
            "generation_date": date.today().isoformat(),
            "references": [
                "C(n+1) inhomogeneous deformation, docs/math/C_inhomogeneous_definition.md",
                "C(n+1) Schema 1, docs/json_schema_specification.md",
            ],
        },
    }


def write_gamma_schema(
    n: int,
    schema1_dir: str | Path = "data",
    output_dir: str | Path = "data",
) -> Path:
    """Generate and write C_n gamma JSON after validating its Schema 1 base."""
    schema1_path = Path(schema1_dir) / f"C_{n}_structure.json"
    with schema1_path.open(encoding="utf-8") as source:
        schema1 = json.load(source)
    gamma_schema = compute_gamma_schema(n, schema1)
    output_path = Path(output_dir) / f"C_{n}_gamma.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(gamma_schema, indent=2, ensure_ascii=False) + "\n")
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("n", nargs="+", type=int, help="Bosonic rank(s), e.g. 1 2 3")
    parser.add_argument("--schema1-dir", default="data")
    parser.add_argument("--output-dir", default="data")
    args = parser.parse_args()
    for rank in args.n:
        print(write_gamma_schema(rank, args.schema1_dir, args.output_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
