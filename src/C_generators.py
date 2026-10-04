"""Generate C(n+1) oscillator bases and their undeformed structure constants."""

from __future__ import annotations

import argparse
import json
from datetime import date
from fractions import Fraction
from itertools import combinations_with_replacement
from pathlib import Path
from typing import TypeAlias


Word: TypeAlias = tuple[str, ...]
Polynomial: TypeAlias = dict[Word, Fraction]


def _oscillator_order(n: int) -> dict[str, int]:
    labels = ["a_1_p", "a_1_m"]
    for k in range(1, n + 1):
        labels.extend((f"b_{k}_p", f"b_{k}_m"))
    return {label: index for index, label in enumerate(labels)}


def _normal_order_word(word: Word, order: dict[str, int]) -> Polynomial:
    """Normal-order one word using CAR and CCR, with creation before annihilation."""
    for index in range(len(word) - 1):
        left, right = word[index:index + 2]
        if left in {"a_1_p", "a_1_m"} and left == right:
            return {}
        if order[left] <= order[right]:
            continue

        swapped = word[:index] + (right, left) + word[index + 2:]
        if (left, right) == ("a_1_m", "a_1_p"):
            contracted = word[:index] + word[index + 2:]
            result = dict(_normal_order_word(contracted, order))
            for term, coeff in _normal_order_word(swapped, order).items():
                result[term] = result.get(term, Fraction(0)) - coeff
            return {term: coeff for term, coeff in result.items() if coeff}

        if left.startswith("b_") and right.startswith("b_"):
            left_mode = left.split("_")[1]
            right_mode = right.split("_")[1]
            if left_mode == right_mode and left.endswith("_m") and right.endswith("_p"):
                contracted = word[:index] + word[index + 2:]
                result = dict(_normal_order_word(contracted, order))
                for term, coeff in _normal_order_word(swapped, order).items():
                    result[term] = result.get(term, Fraction(0)) + coeff
                return {term: coeff for term, coeff in result.items() if coeff}

        return _normal_order_word(swapped, order)

    return {word: Fraction(1)}


def _add_scaled(target: Polynomial, source: Polynomial, scale: Fraction) -> None:
    for word, coeff in source.items():
        target[word] = target.get(word, Fraction(0)) + scale * coeff
        if not target[word]:
            del target[word]


def _multiply(left: Polynomial, right: Polynomial, order: dict[str, int]) -> Polynomial:
    result: Polynomial = {}
    for left_word, left_coeff in left.items():
        for right_word, right_coeff in right.items():
            ordered = _normal_order_word(left_word + right_word, order)
            _add_scaled(result, ordered, left_coeff * right_coeff)
    return result


def _term(words: tuple[str, ...], coeff: int | Fraction = 1) -> Polynomial:
    return {words: Fraction(coeff)}


def _generator_data(n: int) -> tuple[list[str], list[str], dict[str, Polynomial], dict[str, str]]:
    even: list[str] = [f"H_{k}" for k in range(1, n + 2)]
    odd: list[str] = []
    realizations: dict[str, Polynomial] = {}
    forms: dict[str, str] = {}

    realizations["H_1"] = _term(("a_1_p", "a_1_m")) | _term(("b_1_p", "b_1_m"))
    forms["H_1"] = "a_1^+ a_1^- + b_1^+ b_1^-"
    for k in range(2, n + 1):
        label = f"H_{k}"
        realizations[label] = _term((f"b_{k - 1}_p", f"b_{k - 1}_m")) | _term(
            (f"b_{k}_p", f"b_{k}_m"), -1
        )
        forms[label] = (
            f"b_{k - 1}^+ b_{k - 1}^- - b_{k}^+ b_{k}^-"
        )
    realizations[f"H_{n + 1}"] = _term((f"b_{n}_p", f"b_{n}_m"), -1) | _term((), Fraction(-1, 2))
    forms[f"H_{n + 1}"] = f"-b_{n}^+ b_{n}^- - 1/2"

    for k in range(1, n + 1):
        plus = f"E_2del{k}_p"
        realizations[plus] = _term((f"b_{k}_p", f"b_{k}_p"))
        forms[plus] = f"(b_{k}^+)^2"

    even.extend(f"E_2del{k}_p" for k in range(1, n + 1))
    for k in range(1, n + 1):
        minus = f"E_2del{k}_m"
        realizations[minus] = _term((f"b_{k}_m", f"b_{k}_m"))
        forms[minus] = f"(b_{k}^-)^2"
    even.extend(f"E_2del{k}_m" for k in range(1, n + 1))

    pairs = list((i, j) for i in range(1, n + 1) for j in range(i + 1, n + 1))
    for suffix in ("pp", "mm", "pm", "mp"):
        for i, j in pairs:
            label = f"E_del{i}_del{j}_{suffix}"
            even.append(label)
            first_sign, second_sign = suffix
            first = f"b_{i}_{'p' if first_sign == 'p' else 'm'}"
            second = f"b_{j}_{'p' if second_sign == 'p' else 'm'}"
            realizations[label] = _term((first, second))
            signs = {"p": "+", "m": "-"}
            forms[label] = f"b_{i}^{signs[first_sign]} b_{j}^{signs[second_sign]}"

    for k in range(1, n + 1):
        for suffix in ("pp", "pm", "mp", "mm"):
            label = f"E_eps1_del{k}_{suffix}"
            odd.append(label)
            fermion = f"a_1_{suffix[0]}"
            boson = f"b_{k}_{suffix[1]}"
            realizations[label] = _term((fermion, boson))
            signs = {"p": "+", "m": "-"}
            forms[label] = f"a_1^{signs[suffix[0]]} b_{k}^{signs[suffix[1]]}"

    return even, odd, realizations, forms


def _parity(label: str) -> int:
    return int(label.startswith("E_eps1_"))


def _coeff_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _solve_in_basis(
    target: Polynomial, labels: list[str], realizations: dict[str, Polynomial]
) -> dict[str, Fraction]:
    monomials = sorted(
        set(target).union(*(set(realizations[label]) for label in labels))
    )
    matrix = [
        [realizations[label].get(word, Fraction(0)) for label in labels]
        + [target.get(word, Fraction(0))]
        for word in monomials
    ]
    row = 0
    pivot_rows: list[int] = []
    for column in range(len(labels)):
        pivot = next(
            (candidate for candidate in range(row, len(matrix)) if matrix[candidate][column]),
            None,
        )
        if pivot is None:
            raise ValueError(f"Basis realization is linearly dependent at {labels[column]}")
        matrix[row], matrix[pivot] = matrix[pivot], matrix[row]
        scale = matrix[row][column]
        matrix[row] = [value / scale for value in matrix[row]]
        for other in range(len(matrix)):
            if other == row or not matrix[other][column]:
                continue
            factor = matrix[other][column]
            matrix[other] = [
                current - factor * pivot_value
                for current, pivot_value in zip(matrix[other], matrix[row])
            ]
        pivot_rows.append(row)
        row += 1

    if any(not any(line[:-1]) and line[-1] for line in matrix):
        raise ValueError("Oscillator bracket is outside the declared generator basis")
    return {
        label: matrix[pivot_row][-1]
        for label, pivot_row in zip(labels, pivot_rows)
        if matrix[pivot_row][-1]
    }


def _bracket(
    left: Polynomial,
    right: Polynomial,
    left_parity: int,
    right_parity: int,
    order: dict[str, int],
) -> Polynomial:
    result = _multiply(left, right, order)
    sign = -1 if left_parity * right_parity % 2 == 0 else 1
    _add_scaled(result, _multiply(right, left, order), Fraction(sign))
    return result


def generate_schema(n: int) -> dict:
    """Build a complete Schema 1 JSON-compatible object for bosonic rank n."""
    if n < 1:
        raise ValueError("n must be a positive integer")

    even, odd, realizations, forms = _generator_data(n)
    order = _oscillator_order(n)
    basis_order = odd + even
    parity = {label: _parity(label) for label in basis_order}
    constants: list[dict[str, str]] = []

    for left_label, right_label in combinations_with_replacement(basis_order, 2):
        result = _bracket(
            realizations[left_label],
            realizations[right_label],
            parity[left_label],
            parity[right_label],
            order,
        )
        if not result:
            continue
        components = _solve_in_basis(result, basis_order, realizations)
        for output_label, coeff in components.items():
            constants.append(
                {
                    "X": left_label,
                    "Y": right_label,
                    "Z": output_label,
                    "coeff": _coeff_text(coeff),
                    "sign_rule": "graded",
                }
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
                "dimension_formula": "osp(2m|2n) with m=1",
            },
            "dimension": {
                "total": 2 * n * n + 5 * n + 1,
                "even": 2 * n * n + n + 1,
                "odd": 4 * n,
                "formula": {
                    "even": "2n^2 + n + 1",
                    "odd": "4n",
                    "total": "2n^2 + 5n + 1",
                },
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
                "n": n,
                "count": 2 * n,
                "labels": [
                    label
                    for k in range(1, n + 1)
                    for label in (f"b_{k}_p", f"b_{k}_m")
                ],
                "parity": 0,
                "description": f"Bosonic oscillators b_j^± with j=1,...,{n}",
            },
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations for a_1^±",
                "relations": {
                    "conjugate_pair": "{a_1^-, a_1^+} = 1",
                    "same_type": "{a_1^+, a_1^+} = {a_1^-, a_1^-} = 0",
                },
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations for b_i^±",
                "relations": {
                    "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
                    "conjugate_pair": "[b_i^-, b_j^+] = δ_ij",
                },
            },
            "mixed_commutators": {
                "boson_fermion": "[b_i^±, a_1^σ] = 0 for σ in {+, -}"
            },
        },
        "central_elements": {
            "kappa": {
                "parity": 1,
                "central": True,
                "nilpotent": True,
                "relation": "kappa^2 = 0",
            },
            "K": {
                "parity": 0,
                "central": True,
                "identity": True,
                "relation": "K = 1",
            },
        },
        "basis": {
            "even": even,
            "odd": odd,
            "ordering_convention": "PBW: κ < [odd] < [even]; K = 1 is excluded",
        },
        "parity": parity,
        "generator_realization": {
            "description": "Standard form with PBW oscillator ordering",
            "ordering": list(order),
            "realizations": {
                label: {
                    "standard_form": [
                        {"words": list(words), "coeff": _coeff_text(coeff)}
                        for words, coeff in sorted(realizations[label].items())
                    ],
                    "frappat_form": forms[label],
                    "parity": parity[label],
                }
                for label in basis_order
            },
        },
        "structure_constants": constants,
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": date.today().isoformat(),
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "docs/math/Cn1_definition.md",
                "docs/json_schema_specification.md",
            ],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ranks", nargs="+", type=int, default=[1, 2, 3], help="bosonic ranks to generate"
    )
    parser.add_argument("--output-dir", type=Path, default=Path("data"))
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    for n in args.ranks:
        output = args.output_dir / f"C_{n}_structure.json"
        output.write_text(
            json.dumps(generate_schema(n), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"Wrote {output}")


if __name__ == "__main__":
    main()
