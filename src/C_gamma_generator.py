#!/usr/bin/env python3
"""Generate Schema 2 deformation data for C(n+1)."""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

if __package__:
    from .C_generators import _basis_expansion, _variable_key
else:
    from C_generators import _basis_expansion, _variable_key


@lru_cache(maxsize=None)
def _normal_order_deformed(
    word: tuple[str, ...], parameter: str | None = None
) -> tuple[tuple[tuple[str, ...], str | None, Fraction], ...]:
    for index in range(len(word) - 1):
        left, right = word[index:index + 2]
        if _variable_key(left) <= _variable_key(right):
            continue

        swapped = word[:index] + (right, left) + word[index + 2:]
        terms: dict[tuple[tuple[str, ...], str | None], Fraction] = {}
        same_mode = left.split("_")[0:2] == right.split("_")[0:2]
        swap_coefficient = Fraction(
            -1 if same_mode and left.startswith("a_") else 1
        )
        for ordered, gb, coefficient in _normal_order_deformed(swapped, parameter):
            key = (ordered, gb)
            terms[key] = terms.get(key, Fraction()) + swap_coefficient * coefficient

        if same_mode and left.endswith("_m") and right.endswith("_p"):
            contracted = word[:index] + word[index + 2:]
            for ordered, gb, value in _normal_order_deformed(contracted, parameter):
                key = (ordered, gb)
                terms[key] = terms.get(key, Fraction()) + value
        elif (
            parameter is None
            and left.startswith("b_")
            and right.startswith("a_")
        ):
            contracted = word[:index] + word[index + 2:]
            gb = _parameter_label(right, left)
            prefix_parity = sum(variable.startswith("a_") for variable in word[:index]) % 2
            suffix_parity = sum(
                variable.startswith("a_") for variable in word[index + 2:]
            ) % 2
            contraction_sign = Fraction(
                -1 if (prefix_parity + suffix_parity) % 2 else 1
            )
            for ordered, found_gb, value in _normal_order_deformed(
                contracted, gb
            ):
                key = (ordered, found_gb)
                terms[key] = terms.get(key, Fraction()) + contraction_sign * value

        return tuple(
            (monomial, gb, coefficient)
            for (monomial, gb), coefficient in terms.items()
            if coefficient
        )

    fermions = [variable for variable in word if variable.startswith("a_")]
    if len(fermions) != len(set(fermions)):
        return ()
    return ((word, parameter, Fraction(1)),)


def _parameter_label(fermion: str, boson: str) -> str:
    return f"gb_{fermion}_{boson}"


def _read_polynomials(schema: dict) -> dict[str, dict[tuple[str, ...], Fraction]]:
    return {
        label: {
            tuple(term["words"]): Fraction(term["coeff"])
            for term in realization["standard_form"]
        }
        for label, realization
        in schema["generator_realization"]["realizations"].items()
    }


def _multiply_deformed(
    left: dict[tuple[str, ...], Fraction],
    right: dict[tuple[str, ...], Fraction],
) -> dict[tuple[tuple[str, ...], str | None], Fraction]:
    result: dict[tuple[tuple[str, ...], str | None], Fraction] = {}
    for left_word, left_coefficient in left.items():
        for right_word, right_coefficient in right.items():
            for word, parameter, coefficient in _normal_order_deformed(
                left_word + right_word
            ):
                key = (word, parameter)
                result[key] = result.get(key, Fraction()) + (
                    left_coefficient * right_coefficient * coefficient
                )
    return {key: coefficient for key, coefficient in result.items() if coefficient}


def _bracket_deformed(
    left: dict[tuple[str, ...], Fraction],
    right: dict[tuple[str, ...], Fraction],
    left_parity: int,
    right_parity: int,
) -> dict[tuple[tuple[str, ...], str | None], Fraction]:
    sign = -1 if left_parity and right_parity else 1
    result = _multiply_deformed(left, right)
    reverse = _multiply_deformed(right, left)
    for key, coefficient in reverse.items():
        result[key] = result.get(key, Fraction()) - sign * coefficient
    return {key: coefficient for key, coefficient in result.items() if coefficient}


def _polynomial_by_parameter(
    bracket: dict[tuple[tuple[str, ...], str | None], Fraction]
) -> dict[str | None, dict[tuple[str, ...], Fraction]]:
    result: dict[str | None, dict[tuple[str, ...], Fraction]] = {}
    for (word, parameter), coefficient in bracket.items():
        poly = result.setdefault(parameter, {})
        poly[word] = poly.get(word, Fraction()) + coefficient
    return {
        parameter: {word: coefficient for word, coefficient in poly.items() if coefficient}
        for parameter, poly in result.items()
    }


def _fraction(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else str(value)


def _gamma_expression(coefficients: dict[str, Fraction], parameter_order: list[str]) -> str:
    terms: list[str] = []
    for parameter in parameter_order:
        coefficient = coefficients.get(parameter, Fraction())
        if not coefficient:
            continue
        magnitude = _fraction(abs(coefficient))
        if coefficient == 1:
            term = parameter
        elif coefficient == -1:
            term = f"-{parameter}"
        else:
            term = f"{magnitude}*{parameter}"
            if coefficient < 0:
                term = f"-{term}"
        if not terms:
            terms.append(term)
        else:
            terms.append(f" {'+' if coefficient > 0 else '-'} {term.lstrip('-')}")
    return "".join(terms)


def _parse_gamma_expression(expression: str) -> dict[str, Fraction]:
    terms: dict[str, Fraction] = {}
    for term in expression.split(" + "):
        pieces = term.split(" - ")
        for index, piece in enumerate(pieces):
            if not piece:
                continue
            sign = Fraction(-1 if index else 1)
            if piece.startswith("-"):
                sign *= -1
                piece = piece[1:]
            match = re.fullmatch(r"(?:(-?\d+(?:/\d+)?)\*)?(gb_[a-z0-9_]+)", piece)
            if match is None:
                raise ValueError(f"Invalid gamma coefficient expression: {expression}")
            scalar = Fraction(match.group(1)) if match.group(1) else Fraction(1)
            parameter = match.group(2)
            terms[parameter] = terms.get(parameter, Fraction()) + sign * scalar
    return {parameter: value for parameter, value in terms.items() if value}


def _basis_order(schema: dict) -> list[str]:
    return list(schema["generator_realization"]["realizations"])


def _expected_schema1_brackets(schema: dict) -> dict[tuple[str, str, str], Fraction]:
    return {
        (entry["X"], entry["Y"], entry["Z"]): Fraction(entry["coeff"])
        for entry in schema["structure_constants"]
    }


def build_gamma_schema(
    rank: int, structure_schema: dict, generation_date: str | None = None
) -> dict:
    if structure_schema["algebra"]["family"] != "C":
        raise ValueError("Source structure schema is not a C-family schema")
    if structure_schema["algebra"]["n"] != rank:
        raise ValueError("Source structure schema rank does not match")

    labels = _basis_order(structure_schema)
    parity = structure_schema["parity"]
    realization = _read_polynomials(structure_schema)
    basis = [(label, realization[label]) for label in labels]
    gamma_basis = basis + [("K", {(): Fraction(1)})]
    expected = _expected_schema1_brackets(structure_schema)
    base_records: dict[tuple[str, str, str], Fraction] = {}
    parameter_coefficients: dict[
        tuple[str, str, str], dict[str, Fraction]
    ] = {}

    for left_index, left in enumerate(labels):
        for right in labels[left_index:]:
            components = _polynomial_by_parameter(_bracket_deformed(
                realization[left],
                realization[right],
                parity[left],
                parity[right],
            ))
            base_poly = components.pop(None, {})
            if base_poly:
                expanded = _basis_expansion(
                    basis, base_poly, f"base bracket [{left},{right}]"
                )
                for result, coefficient in expanded.items():
                    base_records[(left, right, result)] = coefficient

            for parameter, polynomial in components.items():
                expansion = _basis_expansion(
                    gamma_basis,
                    polynomial,
                    f"gamma bracket [{left},{right}] for {parameter}",
                )
                for result, coefficient in expansion.items():
                    key = (left, right, result)
                    entry = parameter_coefficients.setdefault(key, {})
                    entry[parameter] = entry.get(parameter, Fraction()) + coefficient

    if base_records != expected:
        missing = sorted(set(expected) - set(base_records))[:3]
        extra = sorted(set(base_records) - set(expected))[:3]
        differing = [
            key for key in set(expected) & set(base_records)
            if expected[key] != base_records[key]
        ][:3]
        raise ValueError(
            "Undeformed bracket mismatch with Schema 1; "
            f"missing={missing}, extra={extra}, differing={differing}"
        )

    fermions = ["a_1_p", "a_1_m"]
    bosons = structure_schema["oscillator_generators"]["bosons"]["labels"]
    parameter_matrix = [
        [_parameter_label(fermion, boson) for boson in bosons]
        for fermion in fermions
    ]
    parameter_order = [parameter for row in parameter_matrix for parameter in row]
    gamma_coefficients = []
    for (left, right, result), coefficients in sorted(
        parameter_coefficients.items(),
        key=lambda item: (
            labels.index(item[0][0]),
            labels.index(item[0][1]),
            labels.index(item[0][2]) if item[0][2] in labels else len(labels),
        ),
    ):
        expression = _gamma_expression(coefficients, parameter_order)
        if expression:
            gamma_coefficients.append({
                "X": left,
                "Y": right,
                "Z": result,
                "coeff": expression,
                "sign_rule": "graded",
            })

    for record in gamma_coefficients:
        if not set(_parse_gamma_expression(record["coeff"])) <= set(parameter_order):
            raise ValueError(f"Unknown deformation parameter in {record}")

    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": rank,
            "cartan_type": f"C({rank + 1})",
        },
        "source_schema": f"C_{rank}_structure.json",
        "gb_matrix": {
            "shape": [2, 2 * rank],
            "rows": fermions,
            "columns": bosons,
            "entries": parameter_matrix,
            "parameter_parity": 1,
        },
        "inhomogeneous_deformation": {
            "description": (
                "First-order deformation from mixed fermion-boson oscillator "
                "exchange relations"
            ),
            "exchange_relations": [
                f"[{boson}, {fermion}] = -{_parameter_label(fermion, boson)} * kappa"
                for fermion in fermions
                for boson in bosons
            ],
            "bracket_convention": (
                "[X,Y]_gamma = [X,Y]_0 + kappa * gamma(X,Y); "
                "gamma coefficients are linear in gb"
            ),
            "gamma_coefficients": gamma_coefficients,
        },
        "metadata": {
            "generated_by": "src/C_gamma_generator.py",
            "generation_date": generation_date or date.today().isoformat(),
            "references": [
                "docs/math/C_inhomogeneous_definition.md",
                f"C_{rank}_structure.json",
            ],
        },
    }


def validate_consistency(gamma_schema: dict, structure_schema: dict) -> None:
    rank = structure_schema["algebra"]["n"]
    if gamma_schema["source_schema"] != f"C_{rank}_structure.json":
        raise ValueError("Gamma schema references the wrong Schema 1 file")
    if gamma_schema["gb_matrix"]["shape"] != [2, 2 * rank]:
        raise ValueError("gb_matrix has an invalid shape")
    if len(gamma_schema["gb_matrix"]["entries"]) != 2 or any(
        len(row) != 2 * rank for row in gamma_schema["gb_matrix"]["entries"]
    ):
        raise ValueError("gb_matrix entries do not match the declared shape")
    basis = set(
        structure_schema["basis"]["even"] + structure_schema["basis"]["odd"]
    ) | {"K"}
    for record in gamma_schema["inhomogeneous_deformation"]["gamma_coefficients"]:
        if not {record["X"], record["Y"], record["Z"]} <= basis:
            raise ValueError(f"Gamma record references a non-basis label: {record}")
        _parse_gamma_expression(record["coeff"])


def write_gamma_schemas(data_dir: Path, ranks: list[int]) -> list[Path]:
    written: list[Path] = []
    for rank in ranks:
        source = data_dir / f"C_{rank}_structure.json"
        with source.open(encoding="utf-8") as stream:
            structure_schema = json.load(stream)
        gamma_schema = build_gamma_schema(rank, structure_schema)
        validate_consistency(gamma_schema, structure_schema)
        output = data_dir / f"C_{rank}_gamma.json"
        output.write_text(json.dumps(gamma_schema, indent=2) + "\n", encoding="utf-8")
        written.append(output)
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--ranks", type=int, nargs="+", default=[1, 2, 3])
    args = parser.parse_args()
    for path in write_gamma_schemas(args.data_dir, args.ranks):
        print(path)


if __name__ == "__main__":
    main()
