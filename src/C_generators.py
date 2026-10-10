#!/usr/bin/env python3
"""Generate Schema 1 structure data for C(n+1) = osp(2|2n)."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import date
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Mapping

Word = tuple[str, ...]
Polynomial = dict[Word, Fraction]


@dataclass(frozen=True)
class AlgebraBasis:
    n: int
    even: tuple[str, ...]
    odd: tuple[str, ...]
    pbw: tuple[str, ...]
    parity: Mapping[str, int]
    realizations: Mapping[str, Polynomial]
    realization_data: Mapping[str, dict[str, object]]


def _frac(value: int | str | Fraction) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(value)


def _add(left: Polynomial, right: Polynomial) -> Polynomial:
    result = left.copy()
    for word, coefficient in right.items():
        result[word] = result.get(word, Fraction()) + coefficient
        if not result[word]:
            del result[word]
    return result


def _scale(polynomial: Polynomial, coefficient: Fraction) -> Polynomial:
    if not coefficient:
        return {}
    return {
        word: value * coefficient
        for word, value in polynomial.items()
        if value * coefficient
    }


def _atom_key(atom: str) -> tuple[int, int]:
    if atom == "a_1_p":
        return (0, 0)
    if atom == "a_1_m":
        return (1, 0)
    match = re.fullmatch(r"b_(\d+)_(p|m)", atom)
    if match is None:
        raise ValueError(f"Unknown oscillator label: {atom}")
    rank, sign = int(match.group(1)), match.group(2)
    return (2 if sign == "p" else 3, rank)


@lru_cache(maxsize=None)
def _normal_order_word(word: Word) -> tuple[tuple[Word, Fraction], ...]:
    """Reduce one oscillator word to CAR/CCR normal order."""
    for index in range(len(word) - 1):
        left, right = word[index], word[index + 1]
        left_key, right_key = _atom_key(left), _atom_key(right)
        is_fermion_pair = left.startswith("a_") and right.startswith("a_")
        is_boson_pair = left.startswith("b_") and right.startswith("b_")

        if is_fermion_pair and left == right:
            return ()

        if left_key > right_key:
            prefix, suffix = word[:index], word[index + 2 :]
            swapped = prefix + (right, left) + suffix
            reordered = _normal_order_word(swapped)
            sign = Fraction(-1) if is_fermion_pair else Fraction(1)
            result = {
                item: coefficient * sign
                for item, coefficient in reordered
                if coefficient * sign
            }

            if is_fermion_pair and left == "a_1_m" and right == "a_1_p":
                contracted = _normal_order_word(prefix + suffix)
                for item, coefficient in contracted:
                    result[item] = result.get(item, Fraction()) + coefficient
            elif is_boson_pair:
                left_mode = int(left.split("_")[1])
                right_mode = int(right.split("_")[1])
                if left_mode == right_mode and left.endswith("_m") and right.endswith("_p"):
                    contracted = _normal_order_word(prefix + suffix)
                    for item, coefficient in contracted:
                        result[item] = result.get(item, Fraction()) + coefficient

            return tuple(
                (item, coefficient)
                for item, coefficient in sorted(result.items())
                if coefficient
            )

    return ((word, Fraction(1)),)


def _normal_order(polynomial: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for word, coefficient in polynomial.items():
        for normalized, factor in _normal_order_word(word):
            result[normalized] = result.get(normalized, Fraction()) + coefficient * factor
    return {word: coefficient for word, coefficient in result.items() if coefficient}


def _multiply(left: Polynomial, right: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for first, first_coefficient in left.items():
        for second, second_coefficient in right.items():
            product = _normal_order_word(first + second)
            for word, factor in product:
                result[word] = (
                    result.get(word, Fraction())
                    + first_coefficient * second_coefficient * factor
                )
    return {word: coefficient for word, coefficient in result.items() if coefficient}


def _poly_from_terms(terms: Iterable[tuple[Iterable[str], int | str]]) -> Polynomial:
    polynomial: Polynomial = {}
    for words, coefficient in terms:
        word = tuple(words)
        for normalized, factor in _normal_order_word(word):
            polynomial[normalized] = (
                polynomial.get(normalized, Fraction())
                + _frac(coefficient) * factor
            )
    return {word: coefficient for word, coefficient in polynomial.items() if coefficient}


def _bracket(
    left: Polynomial, right: Polynomial, left_parity: int, right_parity: int
) -> Polynomial:
    forward = _multiply(left, right)
    reverse = _multiply(right, left)
    return _add(forward, _scale(reverse, Fraction(-1 if not (left_parity * right_parity) else 1)))


def _labels(n: int) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    if n < 1:
        raise ValueError("The bosonic rank n must be a positive integer.")

    even = [f"H_{index}" for index in range(1, n + 2)]
    even.extend(
        label
        for rank in range(1, n + 1)
        for label in (f"E_2del{rank}_p", f"E_2del{rank}_m")
    )
    even.extend(
        f"E_del{first}_del{second}_{suffix}"
        for first in range(1, n + 1)
        for second in range(first + 1, n + 1)
        for suffix in ("pp", "pm", "mp", "mm")
    )
    odd = [
        f"E_eps1_del{rank}_{suffix}"
        for rank in range(1, n + 1)
        for suffix in ("pp", "pm", "mp", "mm")
    ]

    pbw = [
        f"E_eps1_del{rank}_{suffix}"
        for rank in range(1, n + 1)
        for suffix in ("pp", "pm")
    ]
    pbw.extend(
        f"E_eps1_del{rank}_{suffix}"
        for rank in range(1, n + 1)
        for suffix in ("mp", "mm")
    )
    pbw.extend(f"H_{index}" for index in range(1, n + 2))
    pbw.extend(f"E_2del{rank}_p" for rank in range(1, n + 1))
    pbw.extend(
        f"E_del{first}_del{second}_pp"
        for first in range(1, n + 1)
        for second in range(first + 1, n + 1)
    )
    pbw.extend(
        f"E_del{first}_del{second}_pm"
        for first in range(1, n + 1)
        for second in range(first + 1, n + 1)
    )
    pbw.extend(f"E_2del{rank}_m" for rank in range(1, n + 1))
    pbw.extend(
        f"E_del{first}_del{second}_mm"
        for first in range(1, n + 1)
        for second in range(first + 1, n + 1)
    )
    pbw.extend(
        f"E_del{first}_del{second}_mp"
        for first in range(1, n + 1)
        for second in range(first + 1, n + 1)
    )
    return tuple(even), tuple(odd), tuple(pbw)


def _realizations(
    n: int, even: tuple[str, ...], odd: tuple[str, ...]
) -> tuple[dict[str, Polynomial], dict[str, dict[str, object]]]:
    polynomials: dict[str, Polynomial] = {}
    data: dict[str, dict[str, object]] = {}

    def add(
        label: str,
        terms: list[tuple[list[str], str]],
        frappat_form: str,
        parity: int,
        note: str | None = None,
    ) -> None:
        realization: dict[str, object] = {
            "standard_form": [
                {"words": words, "coeff": coefficient}
                for words, coefficient in terms
            ],
            "frappat_form": frappat_form,
            "parity": parity,
        }
        if note is not None:
            realization["note"] = note
        data[label] = realization
        polynomials[label] = _poly_from_terms(terms)

    add(
        "H_1",
        [
            (["a_1_p", "a_1_m"], "1"),
            (["b_1_p", "b_1_m"], "1"),
        ],
        "a_1^+ a_1^- + b_1^+ b_1^-",
        0,
    )
    for rank in range(2, n + 1):
        add(
            f"H_{rank}",
            [
                ([f"b_{rank - 1}_p", f"b_{rank - 1}_m"], "1"),
                ([f"b_{rank}_p", f"b_{rank}_m"], "-1"),
            ],
            f"b_{rank - 1}^+ b_{rank - 1}^- - b_{rank}^+ b_{rank}^-",
            0,
        )
    add(
        f"H_{n + 1}",
        [
            ([f"b_{n}_p", f"b_{n}_m"], "-1"),
            ([], "-1/2"),
        ],
        f"-b_{n}^+ b_{n}^- - 1/2",
        0,
        "Terminal Cartan generator",
    )

    for rank in range(1, n + 1):
        for suffix, sign in (("p", "+"), ("m", "-")):
            add(
                f"E_2del{rank}_{suffix}",
                [([f"b_{rank}_{suffix}", f"b_{rank}_{suffix}"], "1")],
                f"(b_{rank}^{sign})^2",
                0,
            )

    for first in range(1, n + 1):
        for second in range(first + 1, n + 1):
            for suffix, signs in (
                ("pp", ("p", "+", "p", "+")),
                ("pm", ("p", "+", "m", "-")),
                ("mp", ("m", "-", "p", "+")),
                ("mm", ("m", "-", "m", "-")),
            ):
                first_sign, first_mark, second_sign, second_mark = signs
                add(
                    f"E_del{first}_del{second}_{suffix}",
                    [
                        (
                            [f"b_{first}_{first_sign}", f"b_{second}_{second_sign}"],
                            "1",
                        )
                    ],
                    f"b_{first}^{first_mark} b_{second}^{second_mark}",
                    0,
                )

    for rank in range(1, n + 1):
        for suffix, eps_sign, eps_mark, delta_sign, delta_mark in (
            ("pp", "p", "+", "p", "+"),
            ("pm", "p", "+", "m", "-"),
            ("mp", "m", "-", "p", "+"),
            ("mm", "m", "-", "m", "-"),
        ):
            add(
                f"E_eps1_del{rank}_{suffix}",
                [([f"a_1_{eps_sign}", f"b_{rank}_{delta_sign}"], "1")],
                f"a_1^{eps_mark} b_{rank}^{delta_mark}",
                1,
            )

    expected = set(even) | set(odd)
    if set(polynomials) != expected:
        raise RuntimeError("Generator realization labels do not match the basis.")
    return polynomials, data


def build_basis(n: int) -> AlgebraBasis:
    """Build the C(n+1) basis, parity map, PBW sequence, and realizations."""
    even, odd, pbw = _labels(n)
    realizations, realization_data = _realizations(n, even, odd)
    parity = {label: 0 for label in even}
    parity.update({label: 1 for label in odd})
    return AlgebraBasis(
        n=n,
        even=even,
        odd=odd,
        pbw=pbw,
        parity=parity,
        realizations=realizations,
        realization_data=realization_data,
    )


def _express_in_basis(
    target: Polynomial, basis: AlgebraBasis
) -> dict[str, Fraction]:
    labels = basis.pbw
    words = sorted(
        set(target).union(
            *(set(basis.realizations[label]) for label in labels)
        )
    )
    matrix = [
        [
            basis.realizations[label].get(word, Fraction())
            for label in labels
        ]
        + [target.get(word, Fraction())]
        for word in words
    ]

    pivot_row = 0
    pivots: list[int] = []
    for column in range(len(labels)):
        selected = next(
            (
                row
                for row in range(pivot_row, len(matrix))
                if matrix[row][column]
            ),
            None,
        )
        if selected is None:
            continue
        matrix[pivot_row], matrix[selected] = matrix[selected], matrix[pivot_row]
        pivot = matrix[pivot_row][column]
        matrix[pivot_row] = [value / pivot for value in matrix[pivot_row]]
        for row in range(len(matrix)):
            if row == pivot_row or not matrix[row][column]:
                continue
            factor = matrix[row][column]
            matrix[row] = [
                value - factor * pivot_value
                for value, pivot_value in zip(matrix[row], matrix[pivot_row])
            ]
        pivots.append(column)
        pivot_row += 1

    if len(pivots) != len(labels):
        raise ValueError("The oscillator realizations are linearly dependent.")
    if any(not any(row[:-1]) and row[-1] for row in matrix):
        raise ValueError("A graded bracket does not close in the generator basis.")

    coordinates = {labels[column]: matrix[row][-1] for row, column in enumerate(pivots)}
    return {
        label: coefficient
        for label, coefficient in coordinates.items()
        if coefficient
    }


def _format_fraction(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def generate_structure_constants(basis: AlgebraBasis) -> list[dict[str, str]]:
    """Compute all nonzero graded brackets for every ordered generator pair."""
    records: list[dict[str, str]] = []
    for left_label in basis.pbw:
        for right_label in basis.pbw:
            bracket = _bracket(
                basis.realizations[left_label],
                basis.realizations[right_label],
                basis.parity[left_label],
                basis.parity[right_label],
            )
            if not bracket:
                continue
            coordinates = _express_in_basis(bracket, basis)
            for output_label in basis.pbw:
                coefficient = coordinates.get(output_label, Fraction())
                if coefficient:
                    records.append(
                        {
                            "X": left_label,
                            "Y": right_label,
                            "Z": output_label,
                            "coeff": _format_fraction(coefficient),
                            "sign_rule": "graded",
                        }
                    )
    return records


def build_schema(
    basis: AlgebraBasis,
    structure_constants: list[dict[str, str]] | None = None,
    generation_date: str | None = None,
) -> dict[str, object]:
    """Build one rank-specific Schema 1 JSON object."""
    n = basis.n
    if structure_constants is None:
        structure_constants = generate_structure_constants(basis)
    if generation_date is None:
        generation_date = date.today().isoformat()

    boson_labels = [
        label
        for rank in range(1, n + 1)
        for label in (f"b_{rank}_p", f"b_{rank}_m")
    ]
    basis_even = list(basis.even)
    basis_odd = list(basis.odd)
    parity = dict(basis.parity)
    ordering = ", ".join(["a_1_p", "a_1_m", *boson_labels])
    pair_order = (
        "PBW: κ (if represented) < [odd positive] < [odd negative] "
        "< [Cartan] < [positive even] < [negative even]; K = 1 is excluded"
    )

    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n + 1})",
            "alternative_notation": {
                "osp": f"osp(2|{2 * n})",
                "dimension_formula": "osp(2m|2n), m=1",
            },
            "dimension": {
                "total": 2 * n * n + 5 * n + 1,
                "even": 2 * n * n + n + 1,
                "odd": 4 * n,
            },
            "dimension_formula": {
                "even": "2n^2 + n + 1",
                "odd": "4n",
                "total": "2n^2 + 5n + 1",
            },
        },
        "oscillator_generators": {
            "fermions": {
                "m": 1,
                "count": 2,
                "labels": ["a_1_p", "a_1_m"],
                "parity": 1,
                "description": "Standard fermionic pair a_1^+, a_1^-",
            },
            "bosons": {
                "count": 2 * n,
                "n": n,
                "labels": boson_labels,
                "parity": 0,
                "description": "Bosonic oscillators b_k^± for k=1,...,n",
            },
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations for the fermion pair",
                "relations": {
                    "conjugate_pair": "{a_1_m, a_1_p} = 1",
                    "same_type": "{a_1_p, a_1_p} = {a_1_m, a_1_m} = 0",
                },
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations for bosonic oscillators",
                "relations": {
                    "same_type": "[b_i^±, b_j^±] = 0 for all i,j",
                    "conjugate_pair": "[b_i_m, b_j_p] = δ_ij",
                },
            },
            "mixed_commutators": {
                "boson_fermion": "[b_i^±, a_1^±] = 0",
            },
        },
        "central_elements": {
            "kappa": {
                "parity": 1,
                "central": True,
                "nilpotency": "kappa^2 = 0",
            },
            "K": {
                "parity": 0,
                "central": True,
                "value": "1",
            },
        },
        "basis": {
            "even": basis_even,
            "odd": basis_odd,
            "ordering_convention": pair_order,
        },
        "parity": parity,
        "generator_realization": {
            "description": "Standard form with PBW ordering",
            "ordering": ordering,
            "realizations": dict(basis.realization_data),
        },
        "structure_constants": structure_constants,
        "metadata": {
            "generated_by": "C_generators.py",
            "generation_date": generation_date,
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "C(n+1) = osp(2|2n) mathematical definition",
            ],
        },
    }


def generate_files(
    ranks: Iterable[int], output_dir: Path, generation_date: str | None = None
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    generated: list[Path] = []
    for n in ranks:
        basis = build_basis(n)
        schema = build_schema(
            basis,
            generate_structure_constants(basis),
            generation_date=generation_date,
        )
        destination = output_dir / f"C_{n}_structure.json"
        destination.write_text(
            json.dumps(schema, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        generated.append(destination)
    return generated


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ranks",
        type=int,
        nargs="+",
        default=[1, 2, 3],
        help="Bosonic ranks to generate (default: 1 2 3)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data",
        help="Destination directory (default: repository data/)",
    )
    arguments = parser.parse_args()
    for generated_file in generate_files(arguments.ranks, arguments.output_dir):
        print(generated_file)


if __name__ == "__main__":
    main()
