#!/usr/bin/env python3
"""Generate Schema 2 gamma data for the C(n+1) inhomogeneous deformation."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import TypeAlias

import sympy as sp

if __package__:
    from .C_generators import (
        Generator,
        _basis_decomposer,
        _decompose_in_basis,
        build_generators,
    )
else:
    from C_generators import (
        Generator,
        _basis_decomposer,
        _decompose_in_basis,
        build_generators,
    )


Word: TypeAlias = tuple[str, ...]
ParameterMonomial: TypeAlias = tuple[str, ...]
DeformedMonomial: TypeAlias = tuple[Word, ParameterMonomial]
DeformedPolynomial: TypeAlias = dict[DeformedMonomial, sp.Rational]
Polynomial: TypeAlias = dict[Word, sp.Rational]
GammaTerms: TypeAlias = dict[tuple[str, str, str], dict[str, sp.Rational]]

FERMION_P = "a_1_p"
FERMION_M = "a_1_m"
KAPPA = "__kappa__"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"


def _oscillator_order(label: str) -> tuple[int, int, int]:
    if label == KAPPA:
        return (-1, 0, 0)
    if label == FERMION_P:
        return (0, 0, 0)
    if label == FERMION_M:
        return (0, 1, 0)
    family, index, sign = label.split("_")
    if family != "b" or sign not in {"p", "m"}:
        raise ValueError(f"Unknown oscillator label: {label}")
    return (1, int(index), 0 if sign == "p" else 1)


def _boson_parts(label: str) -> tuple[int, str]:
    family, index, sign = label.split("_")
    if family != "b" or sign not in {"p", "m"}:
        raise ValueError(f"Expected a boson label, got {label}")
    return int(index), sign


def _gb_parameter(boson: str, fermion: str) -> str:
    index, sign = _boson_parts(boson)
    fermion_sign = "p" if fermion == FERMION_P else "m"
    return f"gb_a1{fermion_sign}_b{index}{sign}"


def _add_scaled(
    target: DeformedPolynomial,
    source: DeformedPolynomial,
    scale: sp.Rational,
    parameters: ParameterMonomial = (),
) -> None:
    if not scale:
        return
    for (word, source_parameters), coefficient in source.items():
        combined_parameters = tuple(sorted(source_parameters + parameters))
        monomial = (word, combined_parameters)
        updated = target.get(monomial, sp.Rational(0)) + scale * coefficient
        if updated:
            target[monomial] = updated
        else:
            target.pop(monomial, None)


@lru_cache(maxsize=None)
def _normal_order_cached(word: Word) -> tuple[tuple[DeformedMonomial, sp.Rational], ...]:
    for index in range(len(word) - 1):
        left, right = word[index], word[index + 1]
        prefix, suffix = word[:index], word[index + 2 :]

        if left == KAPPA and right == KAPPA:
            return ()

        if right == KAPPA and left != KAPPA:
            result: DeformedPolynomial = {}
            sign = -1 if left in {FERMION_P, FERMION_M} else 1
            swapped = prefix + (KAPPA, left) + suffix
            _add_scaled(
                result,
                dict(_normal_order_cached(swapped)),
                sp.Rational(sign),
            )
            return tuple(sorted(result.items()))

        if left == right and left in {FERMION_P, FERMION_M}:
            return ()

        if left == FERMION_M and right == FERMION_P:
            result = {}
            _add_scaled(
                result,
                dict(_normal_order_cached(prefix + suffix)),
                sp.Rational(1),
            )
            _add_scaled(
                result,
                dict(_normal_order_cached(prefix + (FERMION_P, FERMION_M) + suffix)),
                sp.Rational(-1),
            )
            return tuple(sorted(result.items()))

        if left.startswith("b_") and right in {FERMION_P, FERMION_M}:
            result = {}
            swapped = prefix + (right, left) + suffix
            _add_scaled(
                result,
                dict(_normal_order_cached(swapped)),
                sp.Rational(1),
            )
            parameter = _gb_parameter(left, right)
            contraction = prefix + (KAPPA,) + suffix
            _add_scaled(
                result,
                dict(_normal_order_cached(contraction)),
                sp.Rational(-1),
                (parameter,),
            )
            return tuple(sorted(result.items()))

        if _oscillator_order(left) > _oscillator_order(right):
            result = {}
            swapped = prefix + (right, left) + suffix
            _add_scaled(
                result,
                dict(_normal_order_cached(swapped)),
                sp.Rational(1),
            )

            if left.startswith("b_") and right.startswith("b_"):
                left_index, left_sign = _boson_parts(left)
                right_index, right_sign = _boson_parts(right)
                if left_sign == "m" and right_sign == "p" and left_index == right_index:
                    _add_scaled(
                        result,
                        dict(_normal_order_cached(prefix + suffix)),
                        sp.Rational(1),
                    )
            return tuple(sorted(result.items()))

    return ((((word, ()), sp.Rational(1)),))


def _normal_order(word: Word) -> DeformedPolynomial:
    return dict(_normal_order_cached(word))


def _lift_polynomial(polynomial: Polynomial) -> DeformedPolynomial:
    return {(word, ()): coefficient for word, coefficient in polynomial.items()}


def _multiply(
    left: DeformedPolynomial, right: DeformedPolynomial
) -> DeformedPolynomial:
    result: DeformedPolynomial = {}
    for (left_word, left_parameters), left_coefficient in left.items():
        for (right_word, right_parameters), right_coefficient in right.items():
            _add_scaled(
                result,
                _normal_order(left_word + right_word),
                left_coefficient * right_coefficient,
                tuple(sorted(left_parameters + right_parameters)),
            )
    return result


def _add_polynomials(
    left: DeformedPolynomial,
    right: DeformedPolynomial,
    right_scale: sp.Rational = sp.Rational(1),
) -> DeformedPolynomial:
    result = dict(left)
    _add_scaled(result, right, right_scale)
    return result


def _graded_bracket(left: Generator, right: Generator) -> DeformedPolynomial:
    left_polynomial = _lift_polynomial(left.polynomial)
    right_polynomial = _lift_polynomial(right.polynomial)
    sign = -1 if left.parity and right.parity else 1
    return _add_polynomials(
        _multiply(left_polynomial, right_polynomial),
        _multiply(right_polynomial, left_polynomial),
        sp.Rational(-sign),
    )


def _parameter_names(n: int) -> list[str]:
    return [
        _gb_parameter(f"b_{index}_{sign}", fermion)
        for index in range(1, n + 1)
        for sign in ("p", "m")
        for fermion in (FERMION_P, FERMION_M)
    ]


def _schema1_bracket_map(schema1: dict[str, object]) -> dict[tuple[str, str], dict[str, sp.Rational]]:
    brackets: dict[tuple[str, str], dict[str, sp.Rational]] = {}
    for record in schema1["structure_constants"]:
        pair = (record["X"], record["Y"])
        result = brackets.setdefault(pair, {})
        label = record["Z"]
        if label in result:
            raise ValueError(f"Duplicate Schema 1 structure constant for {pair}, {label}.")
        result[label] = sp.Rational(record["coeff"])
    return brackets


def _split_bracket(
    bracket: DeformedPolynomial,
) -> tuple[Polynomial, dict[str, Polynomial]]:
    undeformed: Polynomial = {}
    corrections: dict[str, Polynomial] = defaultdict(dict)
    for (word, parameters), coefficient in bracket.items():
        kappa_count = word.count(KAPPA)
        if kappa_count == 0:
            if parameters:
                raise ValueError("A gb-dependent term is missing κ.")
            undeformed[word] = coefficient
            continue
        if kappa_count != 1 or word[0] != KAPPA:
            raise ValueError("A deformation term must contain one leading κ.")
        if len(parameters) != 1:
            raise ValueError("Only terms linear in gb parameters are allowed.")
        oscillator_word = word[1:]
        polynomial = corrections[parameters[0]]
        updated = polynomial.get(oscillator_word, sp.Rational(0)) + coefficient
        if updated:
            polynomial[oscillator_word] = updated
        else:
            polynomial.pop(oscillator_word, None)
    return undeformed, dict(corrections)


def _check_schema1_compatibility(
    undeformed: Polynomial,
    expected_bracket: dict[str, sp.Rational],
    ordered_generators: list[Generator],
    monomials: list[Word],
    pivot_rows: list[int],
    pivot_inverse: sp.Matrix,
) -> None:
    coefficients = _decompose_in_basis(
        undeformed,
        ordered_generators,
        monomials,
        pivot_rows,
        pivot_inverse,
    )
    actual = {
        generator.label: coefficient
        for generator, coefficient in zip(ordered_generators, coefficients)
        if coefficient
    }
    if actual != expected_bracket:
        raise ValueError(
            f"Deformed bracket's undeformed part disagrees with Schema 1: "
            f"expected {expected_bracket}, got {actual}."
        )


def _format_gamma_coefficient(terms: dict[str, sp.Rational], parameter_order: list[str]) -> str:
    pieces: list[str] = []
    for parameter in parameter_order:
        coefficient = terms.get(parameter, sp.Rational(0))
        if not coefficient:
            continue
        if coefficient == 1:
            pieces.append(parameter)
        elif coefficient == -1:
            pieces.append(f"-{parameter}")
        else:
            pieces.append(f"{coefficient}*{parameter}")
    return " + ".join(pieces).replace("+ -", "- ")


def _parse_gamma_coefficient(
    expression: str, parameter_order: list[str]
) -> dict[str, sp.Rational]:
    parameter_set = set(parameter_order)
    terms: dict[str, sp.Rational] = {}
    for piece in expression.replace("- ", "+ -").split(" + "):
        piece = piece.strip()
        if not piece:
            continue
        sign = -1 if piece.startswith("-") else 1
        unsigned = piece[1:] if sign < 0 else piece
        if "*" in unsigned:
            coefficient_text, parameter = unsigned.split("*", 1)
            coefficient = sp.Rational(coefficient_text)
        else:
            parameter = unsigned
            coefficient = sp.Rational(1)
        if parameter not in parameter_set:
            raise ValueError(f"Malformed gamma coefficient {expression!r}.")
        updated = terms.get(parameter, sp.Rational(0)) + sign * coefficient
        if updated:
            terms[parameter] = updated
        else:
            terms.pop(parameter, None)
    if not terms:
        raise ValueError(f"Gamma coefficient must be nonzero: {expression!r}.")
    return terms


def compute_gamma_coefficients(
    n: int, schema1: dict[str, object]
) -> list[dict[str, str]]:
    """Compute gamma entries, checking their undeformed part against Schema 1."""
    even, odd = build_generators(n)
    ordered_generators = odd + even
    identity = Generator("K", 0, {(): sp.Rational(1)}, "1")
    gamma_output_generators = ordered_generators + [identity]
    schema1_labels = schema1["basis"]["odd"] + schema1["basis"]["even"]
    if schema1_labels != [generator.label for generator in ordered_generators]:
        raise ValueError("Schema 1 basis does not match the approved C(n+1) PBW basis.")
    if schema1["parity"] != {
        generator.label: generator.parity for generator in ordered_generators
    }:
        raise ValueError("Schema 1 parity map does not match the C(n+1) basis.")

    schema1_brackets = _schema1_bracket_map(schema1)
    base_monomials, base_pivot_rows, base_pivot_inverse = _basis_decomposer(
        ordered_generators
    )
    gamma_monomials, gamma_pivot_rows, gamma_pivot_inverse = _basis_decomposer(
        gamma_output_generators
    )
    parameter_order = _parameter_names(n)
    parameter_set = set(parameter_order)
    gamma_terms: GammaTerms = defaultdict(dict)

    for left in ordered_generators:
        for right in ordered_generators:
            bracket = _graded_bracket(left, right)
            undeformed, corrections = _split_bracket(bracket)
            _check_schema1_compatibility(
                undeformed,
                schema1_brackets.get((left.label, right.label), {}),
                ordered_generators,
                base_monomials,
                base_pivot_rows,
                base_pivot_inverse,
            )
            for parameter, polynomial in corrections.items():
                if parameter not in parameter_set:
                    raise ValueError(f"Unexpected gb parameter: {parameter}.")
                coefficients = _decompose_in_basis(
                    polynomial,
                    gamma_output_generators,
                    gamma_monomials,
                    gamma_pivot_rows,
                    gamma_pivot_inverse,
                )
                for generator, coefficient in zip(gamma_output_generators, coefficients):
                    if not coefficient:
                        continue
                    expected_parity = left.parity ^ right.parity ^ 1
                    if generator.parity != expected_parity:
                        raise ValueError(
                            f"Gamma parity mismatch in [{left.label},{right.label}] "
                            f"for output {generator.label}."
                        )
                    key = (left.label, right.label, generator.label)
                    updated = gamma_terms[key].get(parameter, sp.Rational(0)) + coefficient
                    if updated:
                        gamma_terms[key][parameter] = updated
                    else:
                        gamma_terms[key].pop(parameter, None)

    records: list[dict[str, str]] = []
    for left in ordered_generators:
        for right in ordered_generators:
            for generator in gamma_output_generators:
                terms = gamma_terms.get((left.label, right.label, generator.label), {})
                if terms:
                    records.append(
                        {
                            "X": left.label,
                            "Y": right.label,
                            "Z": generator.label,
                            "coeff": _format_gamma_coefficient(terms, parameter_order),
                            "sign_rule": "graded",
                        }
                    )
    _verify_gamma_antisymmetry(records, gamma_output_generators, parameter_order)
    _verify_gamma_cocycle(
        records,
        ordered_generators,
        schema1_brackets,
        parameter_order,
    )
    return records


def _verify_gamma_antisymmetry(
    records: list[dict[str, str]],
    ordered_generators: list[Generator],
    parameter_order: list[str],
) -> None:
    parity = {generator.label: generator.parity for generator in ordered_generators}
    gamma: dict[tuple[str, str, str], dict[str, sp.Rational]] = {}
    for record in records:
        gamma[(record["X"], record["Y"], record["Z"])] = _parse_gamma_coefficient(
            record["coeff"], parameter_order
        )

    for left in ordered_generators:
        for right in ordered_generators:
            sign = -1 if left.parity and right.parity else 1
            for output in ordered_generators:
                forward = gamma.get((left.label, right.label, output.label), {})
                reverse = gamma.get((right.label, left.label, output.label), {})
                expected_reverse = {
                    parameter: -sign * coefficient
                    for parameter, coefficient in forward.items()
                    if coefficient
                }
                if reverse != expected_reverse:
                    raise ValueError(
                        f"Gamma graded anti-symmetry failed for "
                        f"({left.label}, {right.label}, {output.label})."
                    )


def _verify_gamma_cocycle(
    records: list[dict[str, str]],
    ordered_generators: list[Generator],
    schema1_brackets: dict[tuple[str, str], dict[str, sp.Rational]],
    parameter_order: list[str],
) -> int:
    gamma: dict[tuple[str, str], dict[str, dict[str, sp.Rational]]] = {}
    for record in records:
        gamma.setdefault((record["X"], record["Y"]), {})[record["Z"]] = (
            _parse_gamma_coefficient(record["coeff"], parameter_order)
        )
    parity = {generator.label: generator.parity for generator in ordered_generators}
    labels = [generator.label for generator in ordered_generators]
    checks = 0

    for x in labels:
        for y in labels:
            for z in labels:
                total: dict[tuple[str, str], sp.Rational] = {}
                cyclic_terms = (
                    (-1 if parity[x] * parity[z] else 1, x, y, z),
                    (-1 if parity[y] * parity[x] else 1, y, z, x),
                    (-1 if parity[z] * parity[y] else 1, z, x, y),
                )
                for cyclic_sign, outer, first, second in cyclic_terms:
                    base_inner = schema1_brackets.get((first, second), {})
                    for intermediate, base_coefficient in base_inner.items():
                        for output, parameters in gamma.get(
                            (outer, intermediate), {}
                        ).items():
                            for parameter, coefficient in parameters.items():
                                key = (output, parameter)
                                total[key] = total.get(key, sp.Rational(0)) + (
                                    cyclic_sign * base_coefficient * coefficient
                                )
                                if not total[key]:
                                    total.pop(key)

                    for output, parameters in gamma.get((first, second), {}).items():
                        if output == "K":
                            continue
                        outer_sign = -1 if parity[outer] else 1
                        for parameter, coefficient in parameters.items():
                            for result, base_coefficient in schema1_brackets.get(
                                (outer, output), {}
                            ).items():
                                key = (result, parameter)
                                total[key] = total.get(key, sp.Rational(0)) + (
                                    cyclic_sign
                                    * outer_sign
                                    * coefficient
                                    * base_coefficient
                                )
                                if not total[key]:
                                    total.pop(key)
                if total:
                    raise ValueError(
                        f"Gamma cocycle condition failed for ({x}, {y}, {z}): {total}."
                    )
                checks += 1
    return checks


def build_gamma_schema(
    n: int,
    data_dir: Path | None = None,
    generation_date: str | None = None,
) -> dict[str, object]:
    if n not in {1, 2, 3}:
        raise ValueError("This generator supports bosonic ranks n=1, 2, and 3.")
    root = data_dir or DATA_DIR
    schema1_path = root / f"C_{n}_structure.json"
    schema1 = json.loads(schema1_path.read_text(encoding="utf-8"))
    parameters = _parameter_names(n)
    columns = [
        label
        for index in range(1, n + 1)
        for label in (f"b_{index}_p", f"b_{index}_m")
    ]
    entries = [
        [
            _gb_parameter(column, fermion)
            for column in columns
        ]
        for fermion in (FERMION_P, FERMION_M)
    ]
    if sorted(parameter for row in entries for parameter in row) != sorted(parameters):
        raise ValueError("The gb matrix does not contain every approved parameter exactly once.")
    return {
        "schema_version": "5.0",
        "algebra": schema1["algebra"],
        "inhomogeneous_deformation": {
            "output_space": "Schema 1 basis plus central identity K.",
            "gb_matrix": {
                "rows": [FERMION_P, FERMION_M],
                "columns": columns,
                "entries": entries,
                "parity": 0,
            },
            "deformed_oscillator_relations": {
                "description": "The undeformed CAR and CCR are retained; only mixed fermion-boson commutators are deformed.",
                "relation": "[b_j^s, a_1^σ] = -gb_{σ,j,s} κ",
                "gb_parity": 0,
                "kappa_parity": 1,
                "kappa_ordering": "κ is placed to the left of each gamma expression.",
                "truncation": "Retain terms linear in κ and gb; κ^2 = 0.",
            },
            "gamma_coefficients": compute_gamma_coefficients(n, schema1),
        },
        "metadata": {
            "generated_by": "build_C_gamma.py",
            "generation_date": generation_date or date.today().isoformat(),
            "references": [
                "docs/math/C_inhomogeneous_definition.md",
                "docs/math/Cn1_definition.md",
                f"data/C_{n}_structure.json",
            ],
        },
    }


def output_path(n: int, data_dir: Path | None = None) -> Path:
    if n not in {1, 2, 3}:
        raise ValueError("This generator supports bosonic ranks n=1, 2, and 3.")
    return (data_dir or DATA_DIR) / f"C_{n}_gamma.json"


def write_gamma_schema(n: int, data_dir: Path | None = None) -> Path:
    schema = build_gamma_schema(n, data_dir)
    path = output_path(n, data_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(schema, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "n",
        type=int,
        nargs="*",
        default=[1, 2, 3],
        help="Bosonic rank(s) to generate (default: 1 2 3).",
    )
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    args = parser.parse_args()
    for rank in args.n:
        print(write_gamma_schema(rank, args.data_dir))


if __name__ == "__main__":
    main()
