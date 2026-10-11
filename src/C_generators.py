#!/usr/bin/env python3
"""Generate Schema 1 structure constants for C(n+1) = osp(2|2n)."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import date
from fractions import Fraction
from functools import lru_cache
from itertools import combinations
from pathlib import Path
from typing import Any, Iterable

Word = tuple[str, ...]
Polynomial = dict[Word, Fraction]

_A_PLUS = "a_1_p"
_A_MINUS = "a_1_m"


def _token_key(token: str) -> tuple[int, int]:
    if token == _A_PLUS:
        return (0, 0)
    if token == _A_MINUS:
        return (1, 0)
    parts = token.split("_")
    if len(parts) != 3 or parts[0] != "b" or parts[2] not in {"p", "m"}:
        raise ValueError(f"Unknown oscillator label: {token}")
    index = int(parts[1])
    return (2 if parts[2] == "p" else 3, index)


def _word_key(word: Word) -> tuple[tuple[int, int], ...]:
    return tuple(_token_key(token) for token in word)


def _combine_terms(*terms: tuple[Iterable[tuple[Word, Fraction]], Fraction]
                   ) -> tuple[tuple[Word, Fraction], ...]:
    combined: Polynomial = {}
    for values, scale in terms:
        for word, coefficient in values:
            total = combined.get(word, Fraction()) + scale * coefficient
            if total:
                combined[word] = total
            else:
                combined.pop(word, None)
    return tuple(sorted(combined.items(), key=lambda item: _word_key(item[0])))


@lru_cache(maxsize=None)
def _normal_order_cached(word: Word) -> tuple[tuple[Word, Fraction], ...]:
    for index in range(len(word) - 1):
        left, right = word[index], word[index + 1]
        prefix, suffix = word[:index], word[index + 2:]

        if left == right and left in {_A_PLUS, _A_MINUS}:
            return ()

        if left == _A_MINUS and right == _A_PLUS:
            contracted = _normal_order_cached(prefix + suffix)
            reordered = _normal_order_cached(prefix + (_A_PLUS, _A_MINUS) + suffix)
            return _combine_terms((contracted, Fraction(1)),
                                  (reordered, Fraction(-1)))

        left_parts = left.split("_")
        right_parts = right.split("_")
        if (len(left_parts) == len(right_parts) == 3
                and left_parts[0] == right_parts[0] == "b"
                and left_parts[2] == "m" and right_parts[2] == "p"):
            reordered = _normal_order_cached(
                prefix + (right, left) + suffix
            )
            if left_parts[1] == right_parts[1]:
                contracted = _normal_order_cached(prefix + suffix)
                return _combine_terms((reordered, Fraction(1)),
                                      (contracted, Fraction(1)))
            return reordered

        if _token_key(left) > _token_key(right):
            reordered = _normal_order_cached(prefix + (right, left) + suffix)
            return reordered

    return ((word, Fraction(1)),)


def normal_order_word(word: Iterable[str]) -> Polynomial:
    """Return the CAR/CCR normal form of one oscillator word."""
    return dict(_normal_order_cached(tuple(word)))


def _add_scaled(target: Polynomial, source: Polynomial, scale: Fraction) -> None:
    for word, coefficient in source.items():
        result = target.get(word, Fraction()) + scale * coefficient
        if result:
            target[word] = result
        else:
            target.pop(word, None)


def _polynomial_from_terms(
    terms: Iterable[tuple[Iterable[str], Fraction]]
) -> Polynomial:
    polynomial: Polynomial = {}
    for words, coefficient in terms:
        for word, normalized_coefficient in normal_order_word(words).items():
            total = polynomial.get(word, Fraction()) + coefficient * normalized_coefficient
            if total:
                polynomial[word] = total
            else:
                polynomial.pop(word, None)
    return polynomial


def multiply(left: Polynomial, right: Polynomial) -> Polynomial:
    """Multiply two oscillator polynomials and normal-order the result."""
    product: Polynomial = {}
    for left_word, left_coefficient in left.items():
        for right_word, right_coefficient in right.items():
            for word, coefficient in normal_order_word(left_word + right_word).items():
                total = product.get(word, Fraction()) + (
                    left_coefficient * right_coefficient * coefficient
                )
                if total:
                    product[word] = total
                else:
                    product.pop(word, None)
    return product


def graded_bracket(
    left: Polynomial,
    right: Polynomial,
    left_parity: int,
    right_parity: int,
) -> Polynomial:
    """Compute [left,right} using the oscillator product."""
    forward = multiply(left, right)
    reverse = multiply(right, left)
    _add_scaled(forward, reverse, Fraction(-1 if left_parity * right_parity == 0 else 1))
    return forward


@dataclass
class Basis:
    even: list[str]
    odd: list[str]
    parity: dict[str, int]
    polynomials: dict[str, Polynomial]
    realizations: dict[str, dict[str, Any]]

    @property
    def pbw_order(self) -> list[str]:
        return self.odd + self.even


def _standard_form(
    terms: Iterable[tuple[Iterable[str], Fraction]]
) -> list[dict[str, Any]]:
    result = []
    for words, coefficient in terms:
        result.append({
            "words": list(words),
            "coeff": str(coefficient),
        })
    return result


def build_basis(n: int) -> Basis:
    """Build the I01 Option A basis, parity map, and oscillator realizations."""
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        raise ValueError("n must be a positive integer")

    pairs = list(combinations(range(1, n + 1), 2))
    even = [f"H_{index}" for index in range(1, n + 2)]
    even.extend(f"E_2del{index}_p" for index in range(1, n + 1))
    even.extend(f"E_del{i}_del{j}_pp" for i, j in pairs)
    even.extend(f"E_del{i}_del{j}_pm" for i, j in pairs)
    even.extend(f"E_2del{index}_m" for index in range(1, n + 1))
    even.extend(f"E_del{i}_del{j}_mm" for i, j in pairs)
    even.extend(f"E_del{i}_del{j}_mp" for i, j in pairs)
    odd = [
        f"E_eps1_del{index}_{suffix}"
        for index in range(1, n + 1)
        for suffix in ("pp", "pm", "mp", "mm")
    ]

    parity = {label: 0 for label in even}
    parity.update({label: 1 for label in odd})
    realizations: dict[str, dict[str, Any]] = {}
    polynomials: dict[str, Polynomial] = {}

    def add_generator(
        label: str,
        generator_parity: int,
        terms: list[tuple[list[str], Fraction]],
        frappat_form: str,
    ) -> None:
        realizations[label] = {
            "standard_form": _standard_form(terms),
            "frappat_form": frappat_form,
            "parity": generator_parity,
        }
        polynomials[label] = _polynomial_from_terms(terms)

    add_generator(
        "H_1", 0,
        [([_A_PLUS, _A_MINUS], Fraction(1)),
         (["b_1_p", "b_1_m"], Fraction(1))],
        "a_1^+ a_1^- + b_1^+ b_1^-",
    )
    for index in range(2, n + 1):
        add_generator(
            f"H_{index}", 0,
            [([f"b_{index - 1}_p", f"b_{index - 1}_m"], Fraction(1)),
             ([f"b_{index}_p", f"b_{index}_m"], Fraction(-1))],
            f"b_{index - 1}^+ b_{index - 1}^- - b_{index}^+ b_{index}^-",
        )
    add_generator(
        f"H_{n + 1}", 0,
        [([f"b_{n}_p", f"b_{n}_m"], Fraction(-1)),
         ([], Fraction(-1, 2))],
        f"-b_{n}^+ b_{n}^- - 1/2",
    )

    for index in range(1, n + 1):
        add_generator(
            f"E_2del{index}_p", 0,
            [([f"b_{index}_p", f"b_{index}_p"], Fraction(1))],
            f"(b_{index}^+)^2",
        )
    for i, j in pairs:
        add_generator(
            f"E_del{i}_del{j}_pp", 0,
            [([f"b_{i}_p", f"b_{j}_p"], Fraction(1))],
            f"b_{i}^+ b_{j}^+",
        )
    for i, j in pairs:
        add_generator(
            f"E_del{i}_del{j}_pm", 0,
            [([f"b_{i}_p", f"b_{j}_m"], Fraction(1))],
            f"b_{i}^+ b_{j}^-",
        )
    for index in range(1, n + 1):
        add_generator(
            f"E_2del{index}_m", 0,
            [([f"b_{index}_m", f"b_{index}_m"], Fraction(1))],
            f"(b_{index}^-)^2",
        )
    for i, j in pairs:
        add_generator(
            f"E_del{i}_del{j}_mm", 0,
            [([f"b_{i}_m", f"b_{j}_m"], Fraction(1))],
            f"b_{i}^- b_{j}^-",
        )
    for i, j in pairs:
        add_generator(
            f"E_del{i}_del{j}_mp", 0,
            [([f"b_{i}_m", f"b_{j}_p"], Fraction(1))],
            f"b_{i}^- b_{j}^+",
        )

    for index in range(1, n + 1):
        for suffix, fermion, boson_sign, fermion_sign, delta_sign in (
            ("pp", _A_PLUS, "p", "+", "+"),
            ("pm", _A_PLUS, "m", "+", "-"),
            ("mp", _A_MINUS, "p", "-", "+"),
            ("mm", _A_MINUS, "m", "-", "-"),
        ):
            add_generator(
                f"E_eps1_del{index}_{suffix}", 1,
                [([fermion, f"b_{index}_{boson_sign}"], Fraction(1))],
                f"a_1^{fermion_sign} b_{index}^{delta_sign}",
            )

    return Basis(even, odd, parity, polynomials, realizations)


class _BasisDecomposer:
    """Precompute exact elimination for repeated bracket decompositions."""

    def __init__(self, labels: list[str], polynomials: dict[str, Polynomial]):
        self.labels = labels
        coordinates = sorted(
            {word for label in labels for word in polynomials[label]},
            key=_word_key,
        )
        if len(coordinates) < len(labels):
            raise ValueError("Generator realizations are not linearly independent")
        self.coordinates = coordinates
        row_count = len(coordinates)
        column_count = len(labels)
        matrix = [
            [polynomials[label].get(word, Fraction()) for label in labels]
            + [Fraction(int(row == column)) for column in range(row_count)]
            for row, word in enumerate(coordinates)
        ]

        pivot_row = 0
        pivot_columns: list[int] = []
        for column in range(column_count):
            selected = next(
                (row for row in range(pivot_row, row_count)
                 if matrix[row][column]),
                None,
            )
            if selected is None:
                continue
            matrix[pivot_row], matrix[selected] = matrix[selected], matrix[pivot_row]
            pivot_value = matrix[pivot_row][column]
            matrix[pivot_row] = [value / pivot_value for value in matrix[pivot_row]]
            for row in range(row_count):
                if row != pivot_row and matrix[row][column]:
                    scale = matrix[row][column]
                    matrix[row] = [
                        value - scale * pivot
                        for value, pivot in zip(matrix[row], matrix[pivot_row])
                    ]
            pivot_columns.append(column)
            pivot_row += 1

        if len(pivot_columns) != column_count:
            raise ValueError("Generator realizations are linearly dependent")
        self.transform = [row[column_count:] for row in matrix]

    def decompose(self, polynomial: Polynomial) -> dict[str, Fraction]:
        unknown_words = set(polynomial) - set(self.coordinates)
        if unknown_words:
            raise ValueError(
                "Bracket contains monomials outside the generator coordinates: "
                f"{sorted(unknown_words, key=_word_key)}"
            )
        vector = [polynomial.get(word, Fraction()) for word in self.coordinates]
        transformed = [
            sum((value * entry for value, entry in zip(row, vector)), Fraction())
            for row in self.transform
        ]
        coefficient_count = len(self.labels)
        if any(transformed[coefficient_count:]):
            residual = {
                word: coefficient
                for word, coefficient in polynomial.items()
                if coefficient
            }
            raise ValueError(
                f"Bracket is outside the generator span; residual input {residual}"
            )
        return {
            label: transformed[index]
            for index, label in enumerate(self.labels)
            if transformed[index]
        }


def compute_bracket_table(
    basis: Basis,
) -> tuple[list[dict[str, str]], dict[tuple[int, int], dict[int, Fraction]]]:
    """Compute nonzero structure constants and the ordered-pair bracket table."""
    labels = basis.pbw_order
    decomposer = _BasisDecomposer(labels, basis.polynomials)
    constants: list[dict[str, str]] = []
    table: dict[tuple[int, int], dict[int, Fraction]] = {}

    for left_index, left_label in enumerate(labels):
        for right_index in range(left_index, len(labels)):
            right_label = labels[right_index]
            bracket = graded_bracket(
                basis.polynomials[left_label],
                basis.polynomials[right_label],
                basis.parity[left_label],
                basis.parity[right_label],
            )
            coefficients = decomposer.decompose(bracket)
            table[(left_index, right_index)] = {
                labels.index(label): coefficient
                for label, coefficient in coefficients.items()
            }
            for output_label in labels:
                coefficient = coefficients.get(output_label, Fraction())
                if coefficient:
                    constants.append({
                        "X": left_label,
                        "Y": right_label,
                        "Z": output_label,
                        "coeff": str(coefficient),
                        "sign_rule": "graded",
                    })
    return constants, table


def _pbw_ordering_convention() -> str:
    return (
        "PBW: κ < [odd: k ascending, pp, pm, mp, mm] < "
        "[even: H_1,...,H_{n+1}; E_2del{k}_p; "
        "E_del{i}_del{j}_pp; E_del{i}_del{j}_pm; E_2del{k}_m; "
        "E_del{i}_del{j}_mm; E_del{i}_del{j}_mp] (K=1 is excluded)"
    )


def generate_schema(n: int, generation_date: str | None = None) -> dict[str, Any]:
    """Generate one complete v5.0 Schema 1 document for C(n+1)."""
    basis = build_basis(n)
    structure_constants, _ = compute_bracket_table(basis)
    even_dimension = 2 * n * n + n + 1
    odd_dimension = 4 * n
    oscillator_order = [_A_PLUS, _A_MINUS]
    oscillator_order.extend(
        label
        for index in range(1, n + 1)
        for label in (f"b_{index}_p", f"b_{index}_m")
    )
    realization_order = basis.pbw_order

    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n + 1})",
            "alternative_notation": {
                "osp": f"osp(2|{2 * n})",
                "dimension_formula": "osp(2m|2n), with m=1",
            },
            "dimension": {
                "total": even_dimension + odd_dimension,
                "even": even_dimension,
                "odd": odd_dimension,
                "formula": {
                    "even": "2n^2+n+1",
                    "odd": "4n",
                    "total": "2n^2+5n+1",
                },
            },
        },
        "oscillator_generators": {
            "fermions": {
                "m": 1,
                "count": 2,
                "labels": [_A_PLUS, _A_MINUS],
                "parity": 1,
                "description": "One standard fermionic pair a_1^+, a_1^-.",
            },
            "bosons": {
                "n": n,
                "count": 2 * n,
                "labels": oscillator_order[2:],
                "parity": 0,
                "description": "Bosonic oscillators b_k^± for k=1,...,n.",
            },
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations for a_1^±.",
                "relations": {
                    "conjugate_pair": "{a_1_m, a_1_p} = {a_1_p, a_1_m} = 1",
                    "same_type": "{a_1_p, a_1_p} = {a_1_m, a_1_m} = 0",
                },
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations for b_k^±.",
                "relations": {
                    "same_type": (
                        "[b_i^+, b_j^+] = [b_i^-, b_j^-] = 0 for all i,j"
                    ),
                    "conjugate_pair": "[b_i^-, b_j^+] = δ_ij",
                },
            },
            "mixed_commutators": {
                "boson_fermion": (
                    "[b_j^s, a_1^σ] = 0 for all j and s,σ in {+,-}"
                ),
            },
        },
        "central_elements": {
            "kappa": {
                "label": "κ",
                "parity": 1,
                "central": True,
                "nilpotent": True,
                "relation": "κ^2 = 0",
                "description": (
                    "Odd central symbol used by the inhomogeneous extension."
                ),
            },
            "K": {
                "label": "K",
                "parity": 0,
                "central": True,
                "identified_with": "1",
                "independent_basis_element": False,
                "description": "Even central identity; excluded from the basis.",
            },
        },
        "basis": {
            "even": basis.even,
            "odd": basis.odd,
            "ordering_convention": _pbw_ordering_convention(),
        },
        "parity": basis.parity,
        "generator_realization": {
            "description": "Standard form with PBW ordering",
            "ordering": ", ".join(oscillator_order),
            "realizations": {
                label: basis.realizations[label]
                for label in realization_order
            },
        },
        "structure_constants": structure_constants,
        "metadata": {
            "generated_by": "C_generators.py",
            "generation_date": generation_date or date.today().isoformat(),
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "Bakalov and Sullivan (2017)",
            ],
        },
    }


def write_schema(
    n: int,
    output_dir: str | Path,
    generation_date: str | None = None,
) -> Path:
    """Generate and write `C_{n}_structure.json`."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    destination = output_path / f"C_{n}_structure.json"
    serialized = json.dumps(
        generate_schema(n, generation_date),
        ensure_ascii=False,
        indent=2,
    )
    destination.write_text(serialized + "\n", encoding="utf-8")
    return destination


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate Schema 1 structure constants for C(n+1)."
    )
    parser.add_argument(
        "--ranks",
        type=int,
        nargs="+",
        default=[1, 2, 3],
        help="Bosonic ranks to generate (default: 1 2 3).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data",
        help="Output directory (default: repository data/).",
    )
    args = parser.parse_args(argv)

    for n in args.ranks:
        destination = write_schema(n, args.output_dir)
        print(f"Wrote {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
