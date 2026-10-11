#!/usr/bin/env python3
"""Generate Schema 2 gamma structures for the C(n+1) deformation."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from fractions import Fraction
from pathlib import Path
from typing import Any

if __package__:
    from .C_generators import (
        Basis,
        Polynomial,
        _BasisDecomposer,
        build_basis,
        normal_order_word,
    )
else:
    from C_generators import (
        Basis,
        Polynomial,
        _BasisDecomposer,
        build_basis,
        normal_order_word,
    )

_A_PLUS = "a_1_p"
_A_MINUS = "a_1_m"


@dataclass
class DeformedPolynomial:
    base: Polynomial = field(default_factory=dict)
    corrections: dict[str, Polynomial] = field(default_factory=dict)


def _token_key(token: str) -> tuple[int, int]:
    if token == _A_PLUS:
        return (0, 0)
    if token == _A_MINUS:
        return (1, 0)
    parts = token.split("_")
    if len(parts) != 3 or parts[0] != "b" or parts[2] not in {"p", "m"}:
        raise ValueError(f"Unknown oscillator label: {token}")
    return (2 if parts[2] == "p" else 3, int(parts[1]))


def _add_scaled(
    target: Polynomial,
    source: Polynomial,
    scale: Fraction,
) -> None:
    for word, coefficient in source.items():
        total = target.get(word, Fraction()) + scale * coefficient
        if total:
            target[word] = total
        else:
            target.pop(word, None)


def _merge_deformed(
    target: DeformedPolynomial,
    source: DeformedPolynomial,
    scale: Fraction,
) -> None:
    _add_scaled(target.base, source.base, scale)
    for parameter, polynomial in source.corrections.items():
        correction = target.corrections.setdefault(parameter, {})
        _add_scaled(correction, polynomial, scale)
        if not correction:
            target.corrections.pop(parameter)


def _parameter_for_mixed_pair(boson: str, fermion: str) -> str:
    boson_parts = boson.split("_")
    fermion_parts = fermion.split("_")
    if (len(boson_parts) != 3 or boson_parts[0] != "b"
            or len(fermion_parts) != 3 or fermion_parts[0] != "a"):
        raise ValueError(f"Invalid mixed oscillator pair: {boson}, {fermion}")
    return (
        f"gb_a{fermion_parts[1]}_{fermion_parts[2]}_"
        f"b{boson_parts[1]}_{boson_parts[2]}"
    )


def normal_order_deformed_word(word: tuple[str, ...]) -> DeformedPolynomial:
    """Normal-order a word through first order in κ*gb."""
    for index in range(len(word) - 1):
        left, right = word[index], word[index + 1]
        prefix, suffix = word[:index], word[index + 2:]

        if left == right and left in {_A_PLUS, _A_MINUS}:
            return DeformedPolynomial()

        if left == _A_MINUS and right == _A_PLUS:
            result = normal_order_deformed_word(prefix + suffix)
            reordered = normal_order_deformed_word(
                prefix + (_A_PLUS, _A_MINUS) + suffix
            )
            _merge_deformed(result, reordered, Fraction(-1))
            return result

        left_parts = left.split("_")
        right_parts = right.split("_")
        if (len(left_parts) == len(right_parts) == 3
                and left_parts[0] == right_parts[0] == "b"
                and left_parts[2] == "m" and right_parts[2] == "p"):
            result = normal_order_deformed_word(prefix + (right, left) + suffix)
            if left_parts[1] == right_parts[1]:
                contracted = normal_order_deformed_word(prefix + suffix)
                _merge_deformed(result, contracted, Fraction(1))
            return result

        if left.startswith("b_") and right.startswith("a_"):
            result = normal_order_deformed_word(prefix + (right, left) + suffix)
            parameter = _parameter_for_mixed_pair(left, right)
            prefix_fermion_count = sum(token.startswith("a_") for token in prefix)
            correction_scale = Fraction(-1 if prefix_fermion_count % 2 == 0 else 1)
            residual = normal_order_word(prefix + suffix)
            correction = result.corrections.setdefault(parameter, {})
            _add_scaled(correction, residual, correction_scale)
            if not correction:
                result.corrections.pop(parameter)
            return result

        if _token_key(left) > _token_key(right):
            return normal_order_deformed_word(prefix + (right, left) + suffix)

    return DeformedPolynomial(base={word: Fraction(1)})


def multiply_deformed(
    left: Polynomial,
    right: Polynomial,
) -> DeformedPolynomial:
    """Multiply oscillator polynomials with the approved mixed relation."""
    result = DeformedPolynomial()
    for left_word, left_coefficient in left.items():
        for right_word, right_coefficient in right.items():
            normalized = normal_order_deformed_word(left_word + right_word)
            _merge_deformed(
                result,
                normalized,
                left_coefficient * right_coefficient,
            )
    return result


def deformed_bracket(
    left: Polynomial,
    right: Polynomial,
    left_parity: int,
    right_parity: int,
) -> DeformedPolynomial:
    """Compute the deformed graded bracket to first order in κ*gb."""
    forward = multiply_deformed(left, right)
    reverse = multiply_deformed(right, left)
    sign = Fraction(-1 if left_parity * right_parity == 0 else 1)
    _merge_deformed(forward, reverse, sign)
    return forward


def _parameter_names(n: int) -> tuple[list[str], list[list[str]]]:
    row_labels = [_A_PLUS, _A_MINUS]
    column_labels = [
        label
        for index in range(1, n + 1)
        for label in (f"b_{index}_p", f"b_{index}_m")
    ]
    matrix = [
        [_parameter_for_mixed_pair(column, row) for column in column_labels]
        for row in row_labels
    ]
    return column_labels, matrix


def _format_gamma_coefficient(
    terms: dict[str, Fraction],
    parameter_order: list[str],
) -> str:
    formatted: list[str] = []
    for parameter in parameter_order:
        coefficient = terms.get(parameter, Fraction())
        if not coefficient:
            continue
        magnitude = abs(coefficient)
        body = parameter if magnitude == 1 else f"{magnitude}*{parameter}"
        if not formatted:
            formatted.append(body if coefficient > 0 else f"-{body}")
        else:
            formatted.append(f" + {body}" if coefficient > 0 else f" - {body}")
    return "".join(formatted)


def _schema1_brackets(
    schema1: dict[str, Any],
    labels: list[str],
) -> dict[tuple[str, str], dict[str, Fraction]]:
    records = schema1.get("structure_constants")
    if not isinstance(records, list):
        raise ValueError("Schema 1 structure_constants must be an array")
    result: dict[tuple[str, str], dict[str, Fraction]] = defaultdict(dict)
    for record in records:
        x, y, z = record["X"], record["Y"], record["Z"]
        if x not in labels or y not in labels or z not in labels:
            raise ValueError(f"Schema 1 record uses an unknown basis label: {record}")
        if z in result[(x, y)]:
            raise ValueError(f"Duplicate Schema 1 structure-constant record: {record}")
        result[(x, y)][z] = Fraction(record["coeff"])
    return result


def compute_gamma_structure(
    basis: Basis,
    schema1: dict[str, Any],
) -> list[dict[str, str]]:
    """Compute all directed gamma coefficients and cross-check Schema 1 parts."""
    labels = basis.pbw_order
    decomposer = _BasisDecomposer(labels, basis.polynomials)
    gamma_output_labels = labels + ["K"]
    gamma_polynomials = {
        **basis.polynomials,
        "K": {(): Fraction(1)},
    }
    gamma_decomposer = _BasisDecomposer(gamma_output_labels, gamma_polynomials)
    schema1_brackets = _schema1_brackets(
        schema1,
        labels,
    )
    gamma_terms: dict[tuple[str, str, str], dict[str, Fraction]] = defaultdict(dict)

    for x in labels:
        for y in labels:
            result = deformed_bracket(
                basis.polynomials[x],
                basis.polynomials[y],
                basis.parity[x],
                basis.parity[y],
            )
            base_coefficients = decomposer.decompose(result.base)
            if base_coefficients != schema1_brackets.get((x, y), {}):
                raise ValueError(
                    f"Undeformed bracket mismatch with Schema 1 for ({x}, {y})"
                )
            for parameter, polynomial in result.corrections.items():
                coefficients = gamma_decomposer.decompose(polynomial)
                for z, coefficient in coefficients.items():
                    target = gamma_terms[(x, y, z)]
                    target[parameter] = target.get(parameter, Fraction()) + coefficient

    _, parameter_matrix = _parameter_names(len(basis.odd) // 4)
    parameter_order = [
        parameter for row in parameter_matrix for parameter in row
    ]
    records: list[dict[str, str]] = []
    for x in labels:
        for y in labels:
            for z in gamma_output_labels:
                coefficient = _format_gamma_coefficient(
                    gamma_terms.get((x, y, z), {}),
                    parameter_order,
                )
                if coefficient:
                    records.append({
                        "X": x,
                        "Y": y,
                        "Z": z,
                        "coeff": coefficient,
                        "sign_rule": "graded",
                    })
    return records


def generate_gamma_schema(
    schema1: dict[str, Any],
    generation_date: str | None = None,
) -> dict[str, Any]:
    """Generate Schema 2 for the rank specified by a Schema 1 document."""
    try:
        n = schema1["algebra"]["n"]
        if schema1["algebra"]["family"] != "C" or schema1["algebra"]["m"] != 1:
            raise ValueError("Schema 1 input must describe C(n+1) with m=1")
    except (KeyError, TypeError) as error:
        raise ValueError(f"Malformed Schema 1 algebra field: {error}") from error
    basis = build_basis(n)
    if schema1["basis"]["even"] != basis.even or schema1["basis"]["odd"] != basis.odd:
        raise ValueError("Schema 1 basis does not match the approved C(n+1) basis")

    column_labels, parameters = _parameter_names(n)
    gamma_structure = compute_gamma_structure(basis, schema1)
    return {
        "schema_version": "5.0",
        "algebra": schema1["algebra"],
        "gb_matrix": {
            "shape": [2, 2 * n],
            "row_labels": [_A_PLUS, _A_MINUS],
            "column_labels": column_labels,
            "parameters": parameters,
            "parity": 0,
        },
        "inhomogeneous_deformation": {
            "exchange_relation": (
                "[b_j^s, a_1^σ] = -gb_{σ,j,s} * κ"
            ),
            "sign_convention": (
                "Literal source relation; gb is an ordinary scalar and κ is "
                "factored on the left after graded reordering."
            ),
            "kappa_parity": 1,
            "deformation_term_parity": 1,
            "gamma_structure": gamma_structure,
        },
        "metadata": {
            "generated_by": "C_gamma.py",
            "schema1_file": f"C_{n}_structure.json",
            "generation_date": generation_date or date.today().isoformat(),
            "references": [
                "C_inhomogeneous_definition.md",
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
            ],
        },
    }


def write_gamma_schema(
    schema1: dict[str, Any],
    output_dir: str | Path,
    generation_date: str | None = None,
) -> Path:
    """Write `C_{n}_gamma.json` next to the Schema 1 data."""
    n = schema1["algebra"]["n"]
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    destination = output_path / f"C_{n}_gamma.json"
    serialized = json.dumps(
        generate_gamma_schema(schema1, generation_date),
        ensure_ascii=False,
        indent=2,
    )
    destination.write_text(serialized + "\n", encoding="utf-8")
    return destination


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate C(n+1) inhomogeneous gamma structures."
    )
    parser.add_argument(
        "--ranks",
        type=int,
        nargs="+",
        default=[1, 2, 3],
        help="Bosonic ranks to generate (default: 1 2 3).",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data",
        help="Directory containing the C_n_structure.json inputs.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data",
        help="Directory for C_n_gamma.json outputs.",
    )
    args = parser.parse_args(argv)

    for n in args.ranks:
        source = args.data_dir / f"C_{n}_structure.json"
        try:
            schema1 = json.loads(source.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            parser.error(f"could not load Schema 1 file {source}: {error}")
        destination = write_gamma_schema(schema1, args.output_dir)
        print(f"Wrote {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
