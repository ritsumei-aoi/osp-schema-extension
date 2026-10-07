#!/usr/bin/env python3
"""Generate exact Schema 2 gamma data for C(n+1) = osp(2|2n)."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import date
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import TypeAlias

if __package__:
    from .C_generators import (
        Monomial,
        Polynomial,
        _Span,
        _add_scaled,
        _bracket,
        _clean,
        _fraction_string,
        _word_polynomial,
        build_basis,
        build_realizations,
        build_schema,
    )
else:
    from C_generators import (
        Monomial,
        Polynomial,
        _Span,
        _add_scaled,
        _bracket,
        _clean,
        _fraction_string,
        _word_polynomial,
        build_basis,
        build_realizations,
        build_schema,
    )


DeformedTerm: TypeAlias = tuple[str | None, Monomial]
DeformedPolynomial: TypeAlias = dict[DeformedTerm, Fraction]


def _monomial_word(monomial: Monomial) -> tuple[str, ...]:
    fermion_p, fermion_m, bosons = monomial
    word = ["a_1_p"] * fermion_p + ["a_1_m"] * fermion_m
    for index, (boson_p, boson_m) in enumerate(bosons, start=1):
        word.extend([f"b_{index}_p"] * boson_p)
        word.extend([f"b_{index}_m"] * boson_m)
    return tuple(word)


def _token_parity(token: str) -> int:
    return int(token.startswith("a_1_"))


def _parse_token(token: str) -> tuple[str, int, str]:
    prefix, index, sign = token.split("_")
    return prefix, int(index), sign


def _normal_form_monomial(word: tuple[str, ...], n: int) -> Monomial:
    fermion_p = sum(token == "a_1_p" for token in word)
    fermion_m = sum(token == "a_1_m" for token in word)
    bosons = [[0, 0] for _ in range(n)]
    for token in word:
        if token.startswith("b_"):
            _, index, sign = _parse_token(token)
            bosons[index - 1][0 if sign == "p" else 1] += 1
    return fermion_p, fermion_m, tuple(tuple(mode) for mode in bosons)


def _merge_deformed(
    target: DeformedPolynomial,
    source: DeformedPolynomial,
    scale: Fraction,
) -> None:
    if not scale:
        return
    for term, coeff in source.items():
        target[term] = target.get(term, Fraction()) + scale * coeff
        if not target[term]:
            del target[term]


def _first_rewrite(word: tuple[str, ...]) -> int | None:
    for index, (left, right) in enumerate(zip(word, word[1:])):
        if left.startswith("a_1_") and right.startswith("a_1_"):
            if left == right or (left == "a_1_m" and right == "a_1_p"):
                return index
        elif left.startswith("b_") and right.startswith("a_1_"):
            return index
        elif left.startswith("b_") and right.startswith("b_"):
            _, left_index, left_sign = _parse_token(left)
            _, right_index, right_sign = _parse_token(right)
            left_key = (left_index, 0 if left_sign == "p" else 1)
            right_key = (right_index, 0 if right_sign == "p" else 1)
            if left_key > right_key:
                return index
    return None


@lru_cache(maxsize=None)
def _normal_order(
    word: tuple[str, ...], n: int, apply_deformation: bool = True
) -> tuple[tuple[DeformedTerm, Fraction], ...]:
    index = _first_rewrite(word)
    if index is None:
        return (((None, _normal_form_monomial(word, n)), Fraction(1)),)

    left, right = word[index : index + 2]
    prefix, suffix = word[:index], word[index + 2 :]
    result: DeformedPolynomial = {}

    if left.startswith("a_1_"):
        if left == right:
            return ()
        _merge_deformed(
            result,
            dict(_normal_order(prefix + suffix, n, apply_deformation)),
            Fraction(1),
        )
        _merge_deformed(
            result,
            dict(
                _normal_order(
                    prefix + (right, left) + suffix, n, apply_deformation
                )
            ),
            Fraction(-1),
        )
    elif right.startswith("a_1_"):
        _merge_deformed(
            result,
            dict(
                _normal_order(
                    prefix + (right, left) + suffix, n, apply_deformation
                )
            ),
            Fraction(1),
        )
        if apply_deformation:
            _, boson_index, boson_sign = _parse_token(left)
            _, _, fermion_sign = _parse_token(right)
            parameter = f"gb_a1_{fermion_sign}_b{boson_index}_{boson_sign}"
            move_sign = -1 if sum(map(_token_parity, prefix)) % 2 else 1
            for (_, monomial), coeff in _normal_order(
                prefix + suffix, n, apply_deformation=False
            ):
                key = (parameter, monomial)
                result[key] = result.get(key, Fraction()) - move_sign * coeff
                if not result[key]:
                    del result[key]
    else:
        _, left_index, left_sign = _parse_token(left)
        _, right_index, right_sign = _parse_token(right)
        _merge_deformed(
            result,
            dict(
                _normal_order(
                    prefix + (right, left) + suffix, n, apply_deformation
                )
            ),
            Fraction(1),
        )
        if left_index == right_index and left_sign == "m" and right_sign == "p":
            _merge_deformed(
                result,
                dict(_normal_order(prefix + suffix, n, apply_deformation)),
                Fraction(1),
            )

    return tuple(
        sorted(result.items(), key=lambda item: (item[0][0] or "", item[0][1]))
    )


def _multiply_deformed(
    left: Polynomial, right: Polynomial, n: int
) -> DeformedPolynomial:
    result: DeformedPolynomial = {}
    for left_monomial, left_coeff in left.items():
        left_word = _monomial_word(left_monomial)
        for right_monomial, right_coeff in right.items():
            right_word = _monomial_word(right_monomial)
            for term, coeff in _normal_order(left_word + right_word, n):
                result[term] = result.get(term, Fraction()) + (
                    left_coeff * right_coeff * coeff
                )
                if not result[term]:
                    del result[term]
    return result


def _bracket_deformed(
    left: Polynomial, right: Polynomial, left_parity: int, right_parity: int, n: int
) -> DeformedPolynomial:
    result = _multiply_deformed(left, right, n)
    reverse = _multiply_deformed(right, left, n)
    sign = Fraction(1 if left_parity * right_parity else -1)
    _merge_deformed(result, reverse, sign)
    return result


def _parameter_order(n: int) -> list[str]:
    return [
        f"gb_a1_{fermion_sign}_b{index}_{boson_sign}"
        for fermion_sign in ("p", "m")
        for index in range(1, n + 1)
        for boson_sign in ("p", "m")
    ]


def _format_symbolic_coefficient(
    coefficients: dict[str, Fraction], parameter_order: list[str]
) -> str:
    terms = []
    for parameter in parameter_order:
        coeff = coefficients.get(parameter, Fraction())
        if not coeff:
            continue
        magnitude = _fraction_string(abs(coeff))
        factor = parameter if magnitude == "1" else f"{magnitude}*{parameter}"
        if not terms:
            terms.append(f"-{factor}" if coeff < 0 else factor)
        else:
            terms.append(f" - {factor}" if coeff < 0 else f" + {factor}")
    return "".join(terms)


def _assert_schema1_compatible(
    n: int, schema1: dict
) -> tuple[list[str], dict[str, dict]]:
    basis = build_basis(n)
    realizations = build_realizations(n, basis)
    expected_names = basis["odd"] + basis["even"]
    if schema1.get("algebra", {}).get("n") != n:
        raise ValueError(f"Schema 1 rank does not match n={n}")
    if schema1.get("basis") != basis:
        raise ValueError(
            f"Schema 1 basis does not match the C(n+1) convention for n={n}"
        )
    if schema1.get("parity") != {
        **{name: 0 for name in basis["even"]},
        **{name: 1 for name in basis["odd"]},
    }:
        raise ValueError(f"Schema 1 parity map is inconsistent for n={n}")
    schema_realizations = schema1.get("generator_realization", {}).get(
        "realizations", {}
    )
    if schema_realizations != {
        name: realizations[name]["schema"] for name in basis["even"] + basis["odd"]
    }:
        raise ValueError(f"Schema 1 realizations are inconsistent for n={n}")
    return expected_names, realizations


def _verify_undeformed_brackets(
    schema1: dict, names: list[str], realizations: dict, n: int
) -> None:
    parity = schema1["parity"]
    basis_span_names = names
    # Structure constants use the same odd-then-even coordinate ordering as the
    # generator that created the Schema 1 files.
    span = _Span(
        [realizations[name]["polynomial"] for name in basis_span_names]
    )
    actual: dict[tuple[str, str, str], Fraction] = defaultdict(Fraction)
    for left_name in names:
        for right_name in names:
            bracket = _bracket_deformed(
                realizations[left_name]["polynomial"],
                realizations[right_name]["polynomial"],
                parity[left_name],
                parity[right_name],
                n,
            )
            base = {
                monomial: coeff
                for (parameter, monomial), coeff in bracket.items()
                if parameter is None and coeff
            }
            for index, coeff in span.coordinates(base).items():
                actual[(left_name, right_name, basis_span_names[index])] += coeff

    expected: dict[tuple[str, str, str], Fraction] = defaultdict(Fraction)
    for entry in schema1.get("structure_constants", []):
        key = (entry["X"], entry["Y"], entry["Z"])
        expected[key] += Fraction(entry["coeff"])
    actual = {key: value for key, value in actual.items() if value}
    expected = {key: value for key, value in expected.items() if value}
    if actual != expected:
        raise ValueError(f"Zero-parameter brackets differ from Schema 1 for n={n}")


def _build_gamma_records(
    n: int,
    names: list[str],
    realizations: dict[str, dict],
    parity: dict[str, int],
) -> list[dict[str, str]]:
    gamma_names = names + ["K"]
    identity = _word_polynomial([], n)
    basis_span = _Span(
        [realizations[name]["polynomial"] for name in names] + [identity]
    )
    parameter_order = _parameter_order(n)
    coefficients: dict[tuple[str, str, str], dict[str, Fraction]] = defaultdict(
        lambda: defaultdict(Fraction)
    )

    for left_name in names:
        for right_name in names:
            bracket = _bracket_deformed(
                realizations[left_name]["polynomial"],
                realizations[right_name]["polynomial"],
                parity[left_name],
                parity[right_name],
                n,
            )
            by_parameter: dict[str, Polynomial] = defaultdict(dict)
            for (parameter, monomial), coeff in bracket.items():
                if parameter is None:
                    continue
                by_parameter[parameter][monomial] = coeff
            for parameter, polynomial in by_parameter.items():
                for index, coeff in basis_span.coordinates(
                    _clean(polynomial)
                ).items():
                    coefficients[(left_name, right_name, gamma_names[index])][
                        parameter
                    ] += coeff

    records = []
    for left_name in names:
        for right_name in names:
            for result_name in gamma_names:
                coefficient = coefficients.get(
                    (left_name, right_name, result_name), {}
                )
                expression = _format_symbolic_coefficient(
                    coefficient, parameter_order
                )
                if expression:
                    records.append(
                        {
                            "X": left_name,
                            "Y": right_name,
                            "Z": result_name,
                            "coeff": expression,
                            "sign_rule": "graded",
                        }
                    )
    return records


def build_gamma_schema(
    n: int,
    schema1: dict | None = None,
    generation_date: str | None = None,
) -> dict:
    """Build Schema 2 gamma data after checking its Schema 1 source."""
    schema1 = schema1 or build_schema(n, generation_date=generation_date)
    names, realizations = _assert_schema1_compatible(n, schema1)
    _verify_undeformed_brackets(schema1, names, realizations, n)
    parity = schema1["parity"]
    boson_columns = [
        f"b_{index}_{sign}"
        for index in range(1, n + 1)
        for sign in ("p", "m")
    ]
    rows = ["a_1_p", "a_1_m"]
    parameters = _parameter_order(n)
    entries = [
        [
            {
                "parameter": f"gb_a1_{fermion_sign}_{column.replace('b_', 'b')}",
                "parity": 0,
            }
            for column in boson_columns
        ]
        for fermion_sign in ("p", "m")
    ]
    deformation = {
        "central_symbol": "kappa",
        "central_parity": 1,
        "parameter_parity": 0,
        "sign_convention": "gram_entry",
        "exchange_relations": [
            {
                "X": column,
                "Y": row,
                "relation": (
                    f"[{column}, {row}] = "
                    f"-{entries[row_index][column_index]['parameter']} * kappa"
                ),
            }
            for row_index, row in enumerate(rows)
            for column_index, column in enumerate(boson_columns)
        ],
        "coefficient_format": (
            "Exact rational linear combinations of the even gb parameters"
        ),
        "gamma_structure": _build_gamma_records(n, names, realizations, parity),
    }
    return {
        "schema_version": schema1["schema_version"],
        "algebra": schema1["algebra"],
        "source_schema": f"C_{n}_structure.json",
        "gb_matrix": {
            "rows": rows,
            "columns": boson_columns,
            "entries": entries,
            "parameter_order": parameters,
        },
        "inhomogeneous_deformation": deformation,
        "metadata": {
            "generated_by": "C_gamma.py",
            "generation_date": generation_date or date.today().isoformat(),
            "references": [
                "C(n+1) inhomogeneous deformation definition",
                f"C_{n}_structure.json",
            ],
        },
    }


def write_gamma_schema(
    n: int,
    output_dir: Path,
    structure_dir: Path | None = None,
    generation_date: str | None = None,
) -> Path:
    structure_dir = structure_dir or output_dir
    structure_path = structure_dir / f"C_{n}_structure.json"
    if not structure_path.is_file():
        raise FileNotFoundError(f"Schema 1 source file not found: {structure_path}")
    schema1 = json.loads(structure_path.read_text(encoding="utf-8"))
    schema = build_gamma_schema(n, schema1, generation_date)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"C_{n}_gamma.json"
    output_path.write_text(
        json.dumps(schema, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate C(n+1) Schema 2 gamma JSON files."
    )
    parser.add_argument(
        "n",
        nargs="*",
        type=int,
        choices=(1, 2, 3),
        default=None,
        help="bosonic rank(s) to generate; defaults to 1, 2, and 3",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "data",
        help="directory for generated gamma JSON files",
    )
    parser.add_argument(
        "--structure-dir",
        type=Path,
        default=None,
        help="directory containing C_n_structure.json source files",
    )
    args = parser.parse_args()
    for n in args.n or (1, 2, 3):
        print(
            write_gamma_schema(
                n,
                args.output_dir,
                args.structure_dir,
            )
        )


if __name__ == "__main__":
    main()
