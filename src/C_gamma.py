#!/usr/bin/env python3
"""Generate first-order inhomogeneous deformation data for C(n+1)."""

from __future__ import annotations

import json
from datetime import date
from fractions import Fraction
from pathlib import Path
from typing import TypeAlias

from C_generators import (
    Polynomial,
    _coordinates,
    _generators,
    _oscillator_order,
)

Word: TypeAlias = tuple[str, ...]
TaggedWord: TypeAlias = tuple[Word, str | None]
DeformedPolynomial: TypeAlias = dict[TaggedWord, Fraction]


def _add(*polynomials: DeformedPolynomial) -> DeformedPolynomial:
    result: DeformedPolynomial = {}
    for polynomial in polynomials:
        for term, coeff in polynomial.items():
            result[term] = result.get(term, Fraction()) + coeff
    return {term: coeff for term, coeff in result.items() if coeff}


def _scale(polynomial: DeformedPolynomial, coeff: Fraction) -> DeformedPolynomial:
    return {
        term: value * coeff
        for term, value in polynomial.items()
        if value * coeff
    }


def _normal_order(word: Word, order: dict[str, int]) -> DeformedPolynomial:
    for index in range(len(word) - 1):
        left, right = word[index:index + 2]
        if left == right and left.startswith("a_1_"):
            return {}
        if order[left] <= order[right]:
            continue
        prefix, suffix = word[:index], word[index + 2:]
        swapped = prefix + (right, left) + suffix

        if left == "a_1_m" and right == "a_1_p":
            return _add(
                _normal_order(prefix + suffix, order),
                _scale(_normal_order(swapped, order), Fraction(-1)),
            )
        if left.startswith("b_") and right.startswith("b_"):
            same_mode = left.split("_")[1] == right.split("_")[1]
            if same_mode and left.endswith("_m") and right.endswith("_p"):
                return _add(
                    _normal_order(prefix + suffix, order),
                    _normal_order(swapped, order),
                )
        if left.startswith("b_") and right.startswith("a_1_"):
            parameter = f"gb_{right}_{left}"
            contraction: DeformedPolynomial = {}
            for (remainder, existing_parameter), coeff in _normal_order(
                prefix + suffix, order
            ).items():
                if existing_parameter is None:
                    contraction[(remainder, parameter)] = -coeff
            return _add(
                _normal_order(swapped, order),
                contraction,
            )
        return _normal_order(swapped, order)
    return {(word, None): Fraction(1)}


def _multiply(
    left: DeformedPolynomial,
    right: DeformedPolynomial,
    order: dict[str, int],
) -> DeformedPolynomial:
    result: DeformedPolynomial = {}
    for (left_word, left_parameter), left_coeff in left.items():
        for (right_word, right_parameter), right_coeff in right.items():
            if left_parameter and right_parameter:
                continue
            existing_parameter = left_parameter or right_parameter
            for (word, relation_parameter), coeff in _normal_order(
                left_word + right_word, order
            ).items():
                if existing_parameter and relation_parameter:
                    continue
                parameter = existing_parameter or relation_parameter
                term = (word, parameter)
                result[term] = (
                    result.get(term, Fraction()) + left_coeff * right_coeff * coeff
                )
    return {term: coeff for term, coeff in result.items() if coeff}


def _as_deformed(polynomial: Polynomial) -> DeformedPolynomial:
    return {(word, None): coeff for word, coeff in polynomial.items()}


def _bracket(
    left: Polynomial,
    right: Polynomial,
    left_parity: int,
    right_parity: int,
    order: dict[str, int],
) -> DeformedPolynomial:
    sign = -1 if left_parity * right_parity else 1
    return _add(
        _multiply(_as_deformed(left), _as_deformed(right), order),
        _scale(
            _multiply(_as_deformed(right), _as_deformed(left), order),
            Fraction(-sign),
        ),
    )


def _parameter_names(n: int) -> list[str]:
    return [
        f"gb_a_1_{fermion_sign}_b_{k}_{boson_sign}"
        for fermion_sign in ("p", "m")
        for k in range(1, n + 1)
        for boson_sign in ("p", "m")
    ]


def generate_gamma_schema(n: int) -> dict[str, object]:
    if n < 1:
        raise ValueError("Bosonic rank n must be at least 1")
    even, odd, realizations = _generators(n)
    basis = even + odd
    coordinate_basis = [*basis, "K"]
    coordinate_realizations = {**realizations, "K": {(): Fraction(1)}}
    parity = {name: int(name in odd) for name in basis}
    order = _oscillator_order(n)
    parameters = _parameter_names(n)
    gamma_coefficients = []

    for index, x in enumerate(basis):
        for y in basis[index:]:
            deformed = _bracket(
                realizations[x], realizations[y], parity[x], parity[y], order
            )
            by_parameter: dict[str, Polynomial] = {}
            for (word, parameter), coeff in deformed.items():
                if parameter is None:
                    continue
                polynomial = by_parameter.setdefault(parameter, {})
                polynomial[word] = polynomial.get(word, Fraction()) + coeff
            for parameter, polynomial in by_parameter.items():
                try:
                    components = _coordinates(
                        polynomial, coordinate_basis, coordinate_realizations
                    )
                except ValueError as error:
                    raise ValueError(
                        f"Gamma correction for [{x}, {y}] with {parameter} "
                        "is outside the declared generator span"
                    ) from error
                for z, coeff in components.items():
                    gamma_coefficients.append({
                        "X": x,
                        "Y": y,
                        "Z": z,
                        "parameter": parameter,
                        "coeff": str(coeff.numerator) if coeff.denominator == 1
                        else f"{coeff.numerator}/{coeff.denominator}",
                    })

    fermions = ["a_1_p", "a_1_m"]
    bosons = [
        label
        for k in range(1, n + 1)
        for label in (f"b_{k}_p", f"b_{k}_m")
    ]
    relations = []
    for fermion_sign in ("p", "m"):
        fermion = f"a_1_{fermion_sign}"
        for k in range(1, n + 1):
            for boson_sign in ("p", "m"):
                boson = f"b_{k}_{boson_sign}"
                parameter = f"gb_{fermion}_{boson}"
                relations.append({
                    "fermion": fermion,
                    "boson": boson,
                    "parameter": parameter,
                    "relation": f"[{boson}, {fermion}] = -{parameter} * kappa",
                })

    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n + 1})",
            "schema1_file": f"C_{n}_structure.json",
        },
        "gb_matrix": {
            "rows": fermions,
            "columns": bosons,
            "shape": [2, 2 * n],
            "parameters": parameters,
            "parity": 1,
        },
        "inhomogeneous_deformation": {
            "description": "First-order deformation under mixed fermion-boson relations",
            "kappa": {"parity": 1, "relation": "kappa^2 = 0"},
            "relation_convention": (
                "[b_j^s, a_1^sigma] = -gb_a_1_sigma_b_j_s * kappa"
            ),
            "relations": relations,
            "gamma_coefficients": gamma_coefficients,
            "gamma_convention": (
                "[X,Y]_gamma = [X,Y]_0 + kappa * gamma(X,Y); "
                "each record gives a coefficient of its named gb parameter"
            ),
            "parity_note": (
                "Coefficients are computed by the literal mixed-relation rule; "
                "the source definitions assign odd parity to both gb and kappa, "
                "whose product's parity convention is not resolved here."
            ),
        },
        "metadata": {
            "generated_by": "src/C_gamma.py",
            "generation_date": date.today().isoformat(),
            "references": [
                "docs/math/C_inhomogeneous_definition.md",
                "docs/json_schema_specification.md",
            ],
        },
    }


def write_gamma_schemas(
    output_dir: Path | str = "data",
    ranks: tuple[int, ...] = (1, 2, 3),
) -> None:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for n in ranks:
        path = output_dir / f"C_{n}_gamma.json"
        path.write_text(
            json.dumps(generate_gamma_schema(n), indent=2) + "\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    write_gamma_schemas()
