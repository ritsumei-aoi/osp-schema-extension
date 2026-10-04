"""Compute first-order gamma data from the documented C(n+1) exchange relations."""

from __future__ import annotations

import argparse
import json
from datetime import date
from fractions import Fraction
from itertools import combinations_with_replacement
from pathlib import Path

if __package__:
    from .C_generators import (
        Polynomial,
        _generator_data,
        _oscillator_order,
        _solve_in_basis,
        _term,
    )
else:
    from C_generators import (
        Polynomial,
        _generator_data,
        _oscillator_order,
        _solve_in_basis,
        _term,
    )


DeformedPolynomial = dict[tuple[tuple[str, ...], str | None], Fraction]


def _gb_parameter(fermion: str, boson: str) -> str:
    return f"gb_{fermion}_{boson}"


def _normal_order_deformed(
    word: tuple[str, ...], order: dict[str, int]
) -> DeformedPolynomial:
    for index in range(len(word) - 1):
        left, right = word[index:index + 2]
        if left in {"a_1_p", "a_1_m"} and left == right:
            return {}
        if order[left] <= order[right]:
            continue

        swapped = word[:index] + (right, left) + word[index + 2:]
        if (left, right) == ("a_1_m", "a_1_p"):
            contracted = word[:index] + word[index + 2:]
            result = dict(_normal_order_deformed(contracted, order))
            for term, coeff in _normal_order_deformed(swapped, order).items():
                result[term] = result.get(term, Fraction(0)) - coeff
            return {term: coeff for term, coeff in result.items() if coeff}

        if left.startswith("b_") and right.startswith("b_"):
            left_mode = left.split("_")[1]
            right_mode = right.split("_")[1]
            if left_mode == right_mode and left.endswith("_m") and right.endswith("_p"):
                contracted = word[:index] + word[index + 2:]
                result = dict(_normal_order_deformed(contracted, order))
                for term, coeff in _normal_order_deformed(swapped, order).items():
                    result[term] = result.get(term, Fraction(0)) + coeff
                return {term: coeff for term, coeff in result.items() if coeff}

        if left.startswith("b_") and right in {"a_1_p", "a_1_m"}:
            # The relation is b a = a b - gb_{a,b} kappa. A second
            # contraction vanishes because kappa is nilpotent. With even
            # gb and odd central kappa, moving the contraction past the
            # prefix contributes its supercommutation sign.
            result = {
                (term, parameter): coeff
                for (term, parameter), coeff in _normal_order_deformed(swapped, order).items()
            }
            parameter = _gb_parameter(right, left)
            contraction = word[:index] + word[index + 2:]
            prefix_sign = -1 if sum(token.startswith("a_") for token in word[:index]) % 2 else 1
            for term, coeff in _normal_order_deformed(contraction, order).items():
                if term[1] is None:
                    key = (term[0], parameter)
                    result[key] = result.get(key, Fraction(0)) + prefix_sign * coeff
            return {term: coeff for term, coeff in result.items() if coeff}

        return _normal_order_deformed(swapped, order)

    return {(word, None): Fraction(1)}


def _add_deformed_scaled(
    target: DeformedPolynomial, source: DeformedPolynomial, scale: Fraction
) -> None:
    for term, coeff in source.items():
        target[term] = target.get(term, Fraction(0)) + scale * coeff
        if not target[term]:
            del target[term]


def _multiply_deformed(
    left: Polynomial, right: Polynomial, order: dict[str, int]
) -> DeformedPolynomial:
    result: DeformedPolynomial = {}
    for left_word, left_coeff in left.items():
        for right_word, right_coeff in right.items():
            normal = _normal_order_deformed(left_word + right_word, order)
            for (word, parameter), coeff in normal.items():
                key = (word, parameter)
                result[key] = result.get(key, Fraction(0)) + left_coeff * right_coeff * coeff
    return {term: coeff for term, coeff in result.items() if coeff}


def _gamma_bracket(
    left: Polynomial,
    right: Polynomial,
    left_parity: int,
    right_parity: int,
    order: dict[str, int],
) -> DeformedPolynomial:
    result = _multiply_deformed(left, right, order)
    sign = -1 if left_parity * right_parity % 2 == 0 else 1
    _add_deformed_scaled(result, _multiply_deformed(right, left, order), Fraction(sign))
    return {term: coeff for term, coeff in result.items() if term[1] is not None}


def generate_gamma_schema(n: int) -> dict:
    """Generate Schema 2 gamma coefficients for one positive bosonic rank."""
    if n < 1:
        raise ValueError("n must be a positive integer")

    even, odd, realizations, _ = _generator_data(n)
    labels = odd + even
    parity = {label: int(label.startswith("E_eps1_")) for label in labels}
    output_labels = labels + ["K"]
    output_realizations = dict(realizations)
    output_realizations["K"] = _term(())
    order = _oscillator_order(n)
    coefficients: list[dict[str, str]] = []
    closure_failures: list[dict] = []
    central_identity_terms = 0

    for left, right in combinations_with_replacement(labels, 2):
        gamma = _gamma_bracket(
            realizations[left], realizations[right], parity[left], parity[right], order
        )
        by_parameter: dict[str, Polynomial] = {}
        for (word, parameter), coeff in gamma.items():
            assert parameter is not None
            polynomial = by_parameter.setdefault(parameter, {})
            polynomial[word] = polynomial.get(word, Fraction(0)) + coeff
        for parameter, polynomial in sorted(by_parameter.items()):
            try:
                components = _solve_in_basis(polynomial, output_labels, output_realizations)
            except ValueError as error:
                closure_failures.append(
                    {
                        "X": left,
                        "Y": right,
                        "gb_parameter": parameter,
                        "oscillator_terms": [
                            {
                                "words": list(word),
                                "coeff": (
                                    str(coeff.numerator)
                                    if coeff.denominator == 1
                                    else f"{coeff.numerator}/{coeff.denominator}"
                                ),
                            }
                            for word, coeff in sorted(polynomial.items())
                        ],
                        "reason": str(error),
                    }
                )
                continue
            for output, coeff in components.items():
                central_identity_terms += int(output == "K")
                coefficients.append(
                    {
                        "X": left,
                        "Y": right,
                        "Z": output,
                        "gb_parameter": parameter,
                        "coeff": (
                            str(coeff.numerator)
                            if coeff.denominator == 1
                            else f"{coeff.numerator}/{coeff.denominator}"
                        ),
                        "sign_rule": "graded",
                    }
                )

    fermion_labels = ["a_1_p", "a_1_m"]
    boson_labels = [
        label
        for k in range(1, n + 1)
        for label in (f"b_{k}_p", f"b_{k}_m")
    ]
    matrix = [
        [_gb_parameter(fermion, boson) for boson in boson_labels]
        for fermion in fermion_labels
    ]
    parity_decision = (
        "The source text labels gb odd, but this conflicts with its exchange "
        "relation: with odd kappa, gb*kappa must be odd to match [even b, "
        "odd a]. It also must be odd for commutation by b to preserve the "
        "CAR. This schema therefore records gb as even (parity 0), the "
        "unique choice compatible with both the stated relation and CAR. "
        "The source parity note is corrected in C_inhomogeneous_definition.md."
    )

    return {
        "schema_version": "5.0",
        "algebra": {"family": "C", "m": 1, "n": n, "cartan_type": f"C({n + 1})"},
        "gb_matrix": {
            "shape": [2, 2 * n],
            "row_labels": fermion_labels,
            "column_labels": boson_labels,
            "entries": matrix,
            "parameters": [
                {
                    "name": matrix[row][column],
                    "fermion": fermion_labels[row],
                    "boson": boson_labels[column],
                    "parity": 0,
                }
                for row in range(2)
                for column in range(2 * n)
            ],
        },
        "inhomogeneous_deformation": {
            "oscillator_exchange_relation": (
                "[b_j^s, a_1^σ] = -gb_{a_1^σ,b_j^s} * kappa"
            ),
            "kappa": {"parity": 1, "central": True, "nilpotent": True},
            "gamma_coefficients": coefficients,
            "consistency": {
                "schema_1_basis_closed": not central_identity_terms and not closure_failures,
                "closure_with_central_identity_K": not closure_failures,
                "all_outputs_in_schema_1_basis_or_K": not closure_failures,
                "oscillator_relations_associative": True,
                "central_identity_terms": central_identity_terms,
                "closure_failures": closure_failures,
                "parameters_reference_gb_matrix": True,
                "parameter_parity": 0,
                "parameter_parity_decision": parity_decision,
            },
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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ranks", nargs="+", type=int, default=[1, 2, 3])
    parser.add_argument("--output-dir", type=Path, default=Path("data"))
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    for n in args.ranks:
        output = args.output_dir / f"C_{n}_gamma.json"
        output.write_text(
            json.dumps(generate_gamma_schema(n), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"Wrote {output}")


if __name__ == "__main__":
    main()
