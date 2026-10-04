#!/usr/bin/env python3
"""Generate Schema 2 deformation parameters and gamma coefficients for C(n+1)."""

from __future__ import annotations

import argparse
import json
from datetime import date
from fractions import Fraction
from pathlib import Path

try:
    from .C_generators import (
        _coordinate_reducer,
        _decompose,
        _fraction_text,
        _make_generators,
        _normal_order,
        build_schema,
    )
except ImportError:
    from C_generators import (  # type: ignore[no-redef]
        _coordinate_reducer,
        _decompose,
        _fraction_text,
        _make_generators,
        _normal_order,
        build_schema,
    )

Monomial = tuple[str, ...]
TaggedPolynomial = dict[tuple[Monomial, str | None], Fraction]
Polynomial = dict[Monomial, Fraction]


def _add_scaled(
    target: TaggedPolynomial,
    source: TaggedPolynomial,
    scale: Fraction = Fraction(1),
) -> None:
    for key, coefficient in source.items():
        value = target.get(key, Fraction(0)) + scale * coefficient
        if value:
            target[key] = value
        else:
            target.pop(key, None)


def _normal_order_deformed(
    word: Monomial,
    token_order: dict[str, int],
    parameters: dict[tuple[str, str], str],
    parameter: str | None = None,
) -> TaggedPolynomial:
    for index in range(len(word) - 1):
        left, right = word[index : index + 2]
        if left == right and left.startswith("a_"):
            return {}
        if token_order[left] <= token_order[right]:
            continue

        prefix, suffix = word[:index], word[index + 2 :]
        if left == "a_1_m" and right == "a_1_p":
            result = _normal_order_deformed(
                prefix + suffix, token_order, parameters, parameter
            )
            _add_scaled(
                result,
                _normal_order_deformed(
                    prefix + (right, left) + suffix,
                    token_order,
                    parameters,
                    parameter,
                ),
                Fraction(-1),
            )
            return result

        if left.startswith("b_") and right.startswith("b_"):
            left_mode, left_sign = left.split("_")[1:]
            right_mode, right_sign = right.split("_")[1:]
            if left_mode == right_mode and left_sign == "m" and right_sign == "p":
                result = _normal_order_deformed(
                    prefix + (right, left) + suffix,
                    token_order,
                    parameters,
                    parameter,
                )
                _add_scaled(
                    result,
                    _normal_order_deformed(
                        prefix + suffix, token_order, parameters, parameter
                    ),
                )
                return result

        if left.startswith("b_") and right.startswith("a_"):
            result = _normal_order_deformed(
                prefix + (right, left) + suffix,
                token_order,
                parameters,
                parameter,
            )
            if parameter is None:
                deformation_parameter = parameters[(right, left)]
                prefix_parity = sum(token.startswith("a_") for token in prefix) % 2
                correction_sign = Fraction(1 if prefix_parity else -1)
                for normal_word, coefficient in _normal_order(
                    prefix + suffix, token_order
                ).items():
                    key = (normal_word, deformation_parameter)
                    value = (
                        result.get(key, Fraction(0))
                        + correction_sign * coefficient
                    )
                    if value:
                        result[key] = value
                    else:
                        result.pop(key, None)
            return result

        return _normal_order_deformed(
            prefix + (right, left) + suffix,
            token_order,
            parameters,
            parameter,
        )

    return {(word, parameter): Fraction(1)}


def _multiply_deformed(
    left: Polynomial,
    right: Polynomial,
    token_order: dict[str, int],
    parameters: dict[tuple[str, str], str],
) -> TaggedPolynomial:
    result: TaggedPolynomial = {}
    for left_word, left_coefficient in left.items():
        for right_word, right_coefficient in right.items():
            normalized = _normal_order_deformed(
                left_word + right_word, token_order, parameters
            )
            _add_scaled(result, normalized, left_coefficient * right_coefficient)
    return result


def _deformed_bracket(
    left: Polynomial,
    right: Polynomial,
    left_parity: int,
    right_parity: int,
    token_order: dict[str, int],
    parameters: dict[tuple[str, str], str],
) -> TaggedPolynomial:
    result = _multiply_deformed(left, right, token_order, parameters)
    _add_scaled(
        result,
        _multiply_deformed(right, left, token_order, parameters),
        Fraction(-1 if left_parity * right_parity == 0 else 1),
    )
    return result


def build_gamma_schema(n: int) -> dict[str, object]:
    if n < 1:
        raise ValueError("Bosonic rank n must be a positive integer")

    base_schema = build_schema(n)
    even, odd, realizations = _make_generators(n)
    pbw_labels = odd + even
    deformation_output_labels = pbw_labels + ["K"]
    deformation_realizations = {**realizations, "K": {(): Fraction(1)}}
    pivots, parity = _coordinate_reducer(
        deformation_output_labels, deformation_realizations
    )
    token_order = {"a_1_p": 0, "a_1_m": 1}
    for k in range(1, n + 1):
        token_order[f"b_{k}_p"] = 2 * k
        token_order[f"b_{k}_m"] = 2 * k + 1

    fermion_labels = ("a_1_p", "a_1_m")
    boson_labels = [
        label
        for k in range(1, n + 1)
        for label in (f"b_{k}_p", f"b_{k}_m")
    ]
    parameter_entries = [
        [f"gb_{fermion}_{boson}" for boson in boson_labels]
        for fermion in fermion_labels
    ]
    parameters = {
        (fermion, boson): f"gb_{fermion}_{boson}"
        for fermion in fermion_labels
        for boson in boson_labels
    }
    parameter_coefficients: dict[
        tuple[str, str, str], dict[str, Fraction]
    ] = {}
    for left_index, left_label in enumerate(pbw_labels):
        for right_label in pbw_labels[left_index:]:
            bracket = _deformed_bracket(
                realizations[left_label],
                realizations[right_label],
                parity[left_label],
                parity[right_label],
                token_order,
                parameters,
            )
            by_parameter: dict[str, Polynomial] = {}
            for (word, parameter), coefficient in bracket.items():
                if parameter is None:
                    continue
                polynomial = by_parameter.setdefault(parameter, {})
                value = polynomial.get(word, Fraction(0)) + coefficient
                if value:
                    polynomial[word] = value
                else:
                    polynomial.pop(word, None)
            for parameter, polynomial in by_parameter.items():
                try:
                    decomposition = _decompose(polynomial, pivots)
                except ValueError as exc:
                    raise ValueError(
                        f"Gamma bracket ({left_label}, {right_label}) for "
                        f"{parameter} is outside the C(n+1) basis: {exc}"
                    ) from exc
                for output_label, coefficient in decomposition.items():
                    key = (left_label, right_label, output_label)
                    coefficients = parameter_coefficients.setdefault(key, {})
                    value = coefficients.get(parameter, Fraction(0)) + coefficient
                    if value:
                        coefficients[parameter] = value
                    else:
                        coefficients.pop(parameter, None)

    gamma_coefficients = [
        {
            "X": x,
            "Y": y,
            "Z": z,
            "coefficients": [
                {"parameter": parameter, "coeff": _fraction_text(coefficient)}
                for parameter, coefficient in sorted(coefficients.items())
            ],
            "sign_rule": "graded",
        }
        for (x, y, z), coefficients in sorted(
            parameter_coefficients.items(),
            key=lambda item: (
                pbw_labels.index(item[0][0]),
                pbw_labels.index(item[0][1]),
                deformation_output_labels.index(item[0][2]),
            ),
        )
        if coefficients
    ]
    deformed_relations = [
        {
            "X": boson,
            "Y": fermion,
            "relation": f"[{boson}, {fermion}] = -{parameters[(fermion, boson)]} * kappa",
        }
        for fermion in fermion_labels
        for boson in boson_labels
    ]
    return {
        "schema_version": "5.0",
        "algebra": base_schema["algebra"],
        "source_schema1": f"C_{n}_structure.json",
        "gb_matrix": {
            "row_labels": list(fermion_labels),
            "column_labels": boson_labels,
            "shape": [2, 2 * n],
            "parity": 0,
            "entries": parameter_entries,
        },
        "inhomogeneous_deformation": {
            "description": "First-order deformation from the standard fermion-boson mixed relations",
            "deformed_mixed_commutators": deformed_relations,
            "gamma_convention": "[X,Y]_gamma = [X,Y]_0 + kappa * gamma(X,Y); coefficients are stored in the stated gb*kappa relation order",
            "gamma_coefficients": gamma_coefficients,
        },
        "metadata": {
            "generated_by": "src/C_gamma_generator.py",
            "generation_date": date.today().isoformat(),
            "references": [
                "docs/math/C_inhomogeneous_definition.md",
                "docs/json_schema_specification.md",
            ],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--n",
        type=int,
        nargs="+",
        default=[1, 2, 3],
        help="bosonic ranks to generate (default: 1 2 3)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data"),
        help="output directory (default: data)",
    )
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for n in args.n:
        output = args.output_dir / f"C_{n}_gamma.json"
        output.write_text(
            json.dumps(build_gamma_schema(n), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"Wrote {output}")


if __name__ == "__main__":
    main()
