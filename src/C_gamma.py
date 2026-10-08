#!/usr/bin/env python3
"""Compute first-order gamma data for the C(n+1) oscillator deformation."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import TypeAlias

if __package__:
    from .C_generators import (
        Generator,
        _fraction_string,
        _solve_in_basis,
        _word_from_monomial,
        build_generators,
    )
else:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.C_generators import (
        Generator,
        _fraction_string,
        _solve_in_basis,
        _word_from_monomial,
        build_generators,
    )

SymbolicTerm: TypeAlias = tuple[tuple[str, ...], str | None, Fraction]
DeformedPolynomial: TypeAlias = dict[
    tuple[tuple[int, ...], str | None], Fraction
]


def _token_rank(token: str) -> int:
    if token == "a_1_p":
        return 0
    if token == "a_1_m":
        return 1
    _, mode, sign = token.split("_")
    return 2 + 2 * (int(mode) - 1) + (sign == "m")


def _tokens_to_monomial(tokens: tuple[str, ...], n: int) -> tuple[int, ...]:
    powers = [0] * (2 + 2 * n)
    for token in tokens:
        if token == "a_1_p":
            powers[0] += 1
        elif token == "a_1_m":
            powers[1] += 1
        else:
            _, mode, sign = token.split("_")
            powers[2 + 2 * (int(mode) - 1) + (sign == "m")] += 1
    return tuple(powers)


def _deformed_normalizer(n: int):
    @lru_cache(maxsize=None)
    def normalize(tokens: tuple[str, ...]) -> tuple[SymbolicTerm, ...]:
        for index in range(len(tokens) - 1):
            left, right = tokens[index:index + 2]
            left_rank, right_rank = _token_rank(left), _token_rank(right)
            prefix, suffix = tokens[:index], tokens[index + 2:]
            if left.startswith("a_") and right.startswith("a_"):
                if left == right:
                    return ()
                if left == "a_1_m" and right == "a_1_p":
                    return (
                        *((word, parameter, coeff) for word, parameter, coeff
                          in normalize(prefix + suffix)),
                        *((word, parameter, -coeff) for word, parameter, coeff
                          in normalize(prefix + (right, left) + suffix)),
                    )
            elif left.startswith("b_") and right.startswith("b_"):
                _, left_mode, left_sign = left.split("_")
                _, right_mode, right_sign = right.split("_")
                if left_mode == right_mode and left_sign == "m" and right_sign == "p":
                    contracted = normalize(prefix + suffix)
                    swapped = normalize(prefix + (right, left) + suffix)
                    return (*contracted, *swapped)
                if left_rank > right_rank:
                    return normalize(prefix + (right, left) + suffix)
            elif left.startswith("b_") and right.startswith("a_"):
                _, mode, boson_sign = left.split("_")
                fermion_sign = "p" if right == "a_1_p" else "m"
                parameter = f"gb_a1_{fermion_sign}_b{mode}_{boson_sign}"
                contracted = tuple(
                    (word, parameter, -coeff)
                    for word, previous, coeff in normalize(prefix + suffix)
                    if previous is None
                )
                swapped = normalize(prefix + (right, left) + suffix)
                return (*swapped, *contracted)
            elif left_rank > right_rank:
                return normalize(prefix + (right, left) + suffix)

        return ((tokens, None, Fraction(1)),)

    return normalize


def _multiply(
    left: DeformedPolynomial,
    right: DeformedPolynomial,
    n: int,
    normalize,
) -> DeformedPolynomial:
    result: DeformedPolynomial = {}
    for (left_monomial, left_parameter), left_coeff in left.items():
        for (right_monomial, right_parameter), right_coeff in right.items():
            if left_parameter and right_parameter:
                continue
            parameter_product = left_parameter or right_parameter
            word = tuple(_word_from_monomial(left_monomial) + _word_from_monomial(right_monomial))
            for normal_word, relation_parameter, relation_coeff in normalize(word):
                if parameter_product and relation_parameter:
                    continue
                parameter = parameter_product or relation_parameter
                monomial = _tokens_to_monomial(normal_word, n)
                key = (monomial, parameter)
                result[key] = result.get(key, Fraction()) + (
                    left_coeff * right_coeff * relation_coeff
                )
                if not result[key]:
                    del result[key]
    return result


def _add(
    target: DeformedPolynomial,
    source: DeformedPolynomial,
    scale: Fraction = Fraction(1),
) -> None:
    for key, coeff in source.items():
        target[key] = target.get(key, 0) + scale * coeff
        if not target[key]:
            del target[key]


def _as_deformed(generator: Generator) -> DeformedPolynomial:
    return {(monomial, None): coeff for monomial, coeff
            in generator.realization.items()}


def _gb_labels(n: int) -> tuple[list[str], list[str], list[list[str]]]:
    fermions = ["a_1_p", "a_1_m"]
    bosons = [label for k in range(1, n + 1)
              for label in (f"b_{k}_p", f"b_{k}_m")]
    matrix = [
        [f"gb_a1_{fermion[-1]}_b{boson.split('_')[1]}_{boson[-1]}"
         for boson in bosons]
        for fermion in fermions
    ]
    return fermions, bosons, matrix


def build_gamma_schema(
    n: int,
    generation_date: str | None = None,
) -> dict:
    if n < 1:
        raise ValueError("bosonic rank n must be positive")
    generators = build_generators(n)
    identity = tuple(0 for _ in next(iter(generators[0].realization)))
    gamma_basis = generators + [Generator("K", 0, {identity: Fraction(1)}, "1")]
    normalize = _deformed_normalizer(n)
    gamma_coefficients = []
    for left_index, left in enumerate(generators):
        left_poly = _as_deformed(left)
        for right in generators[left_index:]:
            right_poly = _as_deformed(right)
            forward = _multiply(left_poly, right_poly, n, normalize)
            reverse = _multiply(right_poly, left_poly, n, normalize)
            sign = -1 if left.parity and right.parity else 1
            _add(forward, reverse, -sign)
            by_parameter: dict[str, dict[tuple[int, ...], Fraction]] = {}
            for (monomial, parameter), coeff in forward.items():
                if parameter is not None and coeff:
                    by_parameter.setdefault(parameter, {})[monomial] = coeff
            by_generator: dict[str, dict[str, Fraction]] = {}
            for parameter, polynomial in by_parameter.items():
                expansion = _solve_in_basis(
                    {monomial: coeff for monomial, coeff in polynomial.items()},
                    gamma_basis,
                )
                for label, coeff in expansion.items():
                    by_generator.setdefault(label, {})[parameter] = coeff
            for label, parameters in by_generator.items():
                gamma_coefficients.append({
                    "X": left.label,
                    "Y": right.label,
                    "Z": label,
                    "terms": [
                        {"parameter": parameter, "coeff": _fraction_string(coeff)}
                        for parameter, coeff in sorted(parameters.items())
                    ],
                })

    fermions, bosons, matrix = _gb_labels(n)
    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n + 1})",
        },
        "gb_matrix": {
            "rows": fermions,
            "columns": bosons,
            "entries": matrix,
            "parameter_parity": 1,
            "shape": [2, 2 * n],
        },
        "inhomogeneous_deformation": {
            "central_symbol": "kappa",
            "source_relations": [
                "[b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa"
            ],
            "bracket_rule": "[X,Y]_gamma = [X,Y]_0 + kappa * gamma(X,Y)",
            "gamma_coefficients": gamma_coefficients,
            "coefficient_convention": (
                "Terms are linear in independent gb parameters; kappa^2 terms are omitted."
            ),
        },
        "metadata": {
            "generated_by": "C_gamma.py",
            "generation_date": generation_date or date.today().isoformat(),
            "source_structure": f"C_{n}_structure.json",
            "references": [
                "docs/math/C_inhomogeneous_definition.md",
                "docs/json_schema_specification.md",
                "docs/gamma_schema_specification.md",
            ],
        },
    }


def generate_files(output_dir: Path, ranks: tuple[int, ...] = (1, 2, 3)) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for n in ranks:
        path = output_dir / f"C_{n}_gamma.json"
        path.write_text(
            json.dumps(build_gamma_schema(n), indent=2) + "\n",
            encoding="utf-8",
        )
        paths.append(path)
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data",
    )
    parser.add_argument("--ranks", type=int, nargs="+", default=(1, 2, 3))
    args = parser.parse_args()
    for path in generate_files(args.output_dir, tuple(args.ranks)):
        print(path)


if __name__ == "__main__":
    main()
