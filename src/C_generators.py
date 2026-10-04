#!/usr/bin/env python3
"""Generate Schema 1 structure constants for C(n+1) = osp(2|2n)."""

from __future__ import annotations

import argparse
import json
from datetime import date
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from typing import TypeAlias


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
Word: TypeAlias = tuple[str, ...]
Polynomial: TypeAlias = dict[Word, Fraction]


def _oscillator_order(n: int) -> dict[str, int]:
    labels = ["a_1_p", "a_1_m"]
    for k in range(1, n + 1):
        labels.extend((f"b_{k}_p", f"b_{k}_m"))
    return {label: index for index, label in enumerate(labels)}


def _normal_order_word(word: Word, order: dict[str, int]) -> Polynomial:
    """Reduce a word using the standard one-pair CAR and bosonic CCR."""
    for index in range(len(word) - 1):
        left, right = word[index : index + 2]
        if left in ("a_1_p", "a_1_m") and left == right:
            return {}
        if order[left] > order[right]:
            swapped = word[:index] + (right, left) + word[index + 2 :]
            if (left, right) == ("a_1_m", "a_1_p"):
                reduced = _normal_order_word(swapped, order)
                reduced = {term: -coefficient for term, coefficient in reduced.items()}
                contracted = _normal_order_word(word[:index] + word[index + 2 :], order)
                _add_scaled(reduced, contracted, Fraction(1))
                return reduced
            if left.startswith("b_") and left.endswith("_m") and right.startswith("b_") and right.endswith("_p"):
                reduced = _normal_order_word(swapped, order)
                left_index = left.split("_")[1]
                right_index = right.split("_")[1]
                if left_index == right_index:
                    contracted = _normal_order_word(word[:index] + word[index + 2 :], order)
                    _add_scaled(reduced, contracted, Fraction(1))
                return reduced
            return _normal_order_word(swapped, order)
    return {word: Fraction(1)}


def _add_scaled(target: Polynomial, source: Polynomial, scale: Fraction) -> None:
    if not scale:
        return
    for word, coefficient in source.items():
        target[word] = target.get(word, Fraction(0)) + scale * coefficient
        if not target[word]:
            del target[word]


def _multiply(left: Polynomial, right: Polynomial, order: dict[str, int]) -> Polynomial:
    result: Polynomial = {}
    for left_word, left_coefficient in left.items():
        for right_word, right_coefficient in right.items():
            normal = _normal_order_word(left_word + right_word, order)
            _add_scaled(result, normal, left_coefficient * right_coefficient)
    return result


def _monomial(*words: str, coefficient: Fraction = Fraction(1)) -> Polynomial:
    return {tuple(words): coefficient}


def _add(*terms: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for term in terms:
        _add_scaled(result, term, Fraction(1))
    return result


def _basis_realizations(n: int) -> tuple[list[str], dict[str, Polynomial], dict[str, int]]:
    realizations: dict[str, Polynomial] = {}
    parity: dict[str, int] = {}

    for k in range(1, n + 1):
        realizations[f"E_2del{k}_m"] = _monomial(
            f"b_{k}_m", f"b_{k}_m", coefficient=Fraction(1, 2)
        )
        realizations[f"E_2del{k}_p"] = _monomial(
            f"b_{k}_p", f"b_{k}_p", coefficient=Fraction(1, 2)
        )
        parity[f"E_2del{k}_m"] = parity[f"E_2del{k}_p"] = 0

    for i, j in combinations(range(1, n + 1), 2):
        for suffix, left_sign, right_sign in (
            ("mm", "m", "m"),
            ("mp", "m", "p"),
            ("pm", "p", "m"),
            ("pp", "p", "p"),
        ):
            label = f"E_del{i}_del{j}_{suffix}"
            realizations[label] = _monomial(f"b_{i}_{left_sign}", f"b_{j}_{right_sign}")
            parity[label] = 0

    realizations["H_1"] = _add(
        _monomial("a_1_p", "a_1_m"),
        _monomial("b_1_p", "b_1_m"),
    )
    parity["H_1"] = 0
    for k in range(2, n + 1):
        label = f"H_{k}"
        realizations[label] = _add(
            _monomial(f"b_{k - 1}_p", f"b_{k - 1}_m"),
            _monomial(f"b_{k}_p", f"b_{k}_m", coefficient=Fraction(-1)),
        )
        parity[label] = 0
    terminal = f"H_{n + 1}"
    realizations[terminal] = _add(
        _monomial(f"b_{n}_p", f"b_{n}_m", coefficient=Fraction(-1)),
        _monomial(coefficient=Fraction(-1, 2)),
    )
    parity[terminal] = 0

    for k in range(1, n + 1):
        for suffix, fermion_sign, boson_sign in (
            ("mp", "m", "p"),
            ("mm", "m", "m"),
            ("pm", "p", "m"),
            ("pp", "p", "p"),
        ):
            label = f"E_eps1_del{k}_{suffix}"
            realizations[label] = _monomial(f"a_1_{fermion_sign}", f"b_{k}_{boson_sign}")
            parity[label] = 1

    even_negative = [
        *(f"E_2del{k}_m" for k in range(1, n + 1)),
        *(
            f"E_del{i}_del{j}_{suffix}"
            for i, j in combinations(range(1, n + 1), 2)
            for suffix in ("mm", "mp")
        ),
    ]
    odd_negative = [
        f"E_eps1_del{k}_{suffix}"
        for k in range(1, n + 1)
        for suffix in ("mp", "mm")
    ]
    cartan = [f"H_{k}" for k in range(1, n + 2)]
    even_positive = [
        *(f"E_2del{k}_p" for k in range(1, n + 1)),
        *(
            f"E_del{i}_del{j}_{suffix}"
            for i, j in combinations(range(1, n + 1), 2)
            for suffix in ("pp", "pm")
        ),
    ]
    odd_positive = [
        f"E_eps1_del{k}_{suffix}"
        for k in range(1, n + 1)
        for suffix in ("pp", "pm")
    ]
    basis = even_negative + odd_negative + cartan + even_positive + odd_positive
    expected = 2 * n * n + n + 1 + 4 * n
    if len(basis) != expected or len(set(basis)) != expected:
        raise ValueError(f"Internal basis construction error for n={n}")
    return basis, realizations, parity


def _graded_bracket(
    left: Polynomial,
    right: Polynomial,
    left_parity: int,
    right_parity: int,
    order: dict[str, int],
) -> Polynomial:
    first = _multiply(left, right, order)
    second = _multiply(right, left, order)
    bracket: Polynomial = {}
    _add_scaled(bracket, first, Fraction(1))
    _add_scaled(bracket, second, Fraction(-1) if not (left_parity and right_parity) else Fraction(1))
    return bracket


def _decompose(
    polynomial: Polynomial,
    basis: list[str],
    realizations: dict[str, Polynomial],
) -> dict[str, Fraction]:
    monomials = sorted(
        set(polynomial).union(*(set(realizations[label]) for label in basis))
    )
    matrix = [
        [realizations[label].get(word, Fraction(0)) for label in basis]
        + [polynomial.get(word, Fraction(0))]
        for word in monomials
    ]
    pivot_row = 0
    pivots: list[int] = []
    for column in range(len(basis)):
        selected = next(
            (row for row in range(pivot_row, len(matrix)) if matrix[row][column]),
            None,
        )
        if selected is None:
            raise ValueError(f"Generator realizations are linearly dependent: {basis[column]}")
        matrix[pivot_row], matrix[selected] = matrix[selected], matrix[pivot_row]
        divisor = matrix[pivot_row][column]
        matrix[pivot_row] = [value / divisor for value in matrix[pivot_row]]
        for row in range(len(matrix)):
            if row == pivot_row or not matrix[row][column]:
                continue
            factor = matrix[row][column]
            matrix[row] = [
                value - factor * pivot
                for value, pivot in zip(matrix[row], matrix[pivot_row])
            ]
        pivots.append(column)
        pivot_row += 1

    for row in matrix[pivot_row:]:
        if any(row[column] for column in range(len(basis))):
            raise ValueError("Failed to reduce structure constant system")
        if row[-1]:
            raise ValueError(f"Bracket is outside the declared basis: {polynomial}")
    return {
        basis[column]: matrix[row][-1]
        for row, column in enumerate(pivots)
        if matrix[row][-1]
    }


def _standard_form(polynomial: Polynomial) -> list[dict[str, object]]:
    return [
        {"words": list(word), "coeff": str(coefficient)}
        for word, coefficient in sorted(polynomial.items())
    ]


def _display_realization(label: str, n: int) -> str:
    if label.startswith("H_"):
        index = int(label.split("_")[1])
        if index == 1:
            return "a_1^+ a_1^- + b_1^+ b_1^-"
        if index <= n:
            return f"b_{index - 1}^+ b_{index - 1}^- - b_{index}^+ b_{index}^-"
        return f"-b_{n}^+ b_{n}^- - 1/2"
    if label.startswith("E_2del"):
        k_and_sign = label.removeprefix("E_2del")
        sign = "+" if k_and_sign.endswith("_p") else "-"
        k = k_and_sign.split("_")[0]
        return f"1/2 (b_{k}^{sign})^2"
    if label.startswith("E_del"):
        _, i_label, j_label, suffix = label.split("_")
        i = i_label.removeprefix("del")
        j = j_label.removeprefix("del")
        signs = {"p": "+", "m": "-"}
        return f"b_{i}^{signs[suffix[0]]} b_{j}^{signs[suffix[1]]}"
    _, _, k_label, suffix = label.split("_")
    k = k_label.removeprefix("del")
    signs = {"p": "+", "m": "-"}
    return f"a_1^{signs[suffix[0]]} b_{k}^{signs[suffix[1]]}"


def _structure_constants(
    basis: list[str],
    realizations: dict[str, Polynomial],
    parity: dict[str, int],
    order: dict[str, int],
) -> list[dict[str, str]]:
    constants: list[dict[str, str]] = []
    for left_index, left_label in enumerate(basis):
        for right_label in basis[left_index:]:
            bracket = _graded_bracket(
                realizations[left_label],
                realizations[right_label],
                parity[left_label],
                parity[right_label],
                order,
            )
            if not bracket:
                continue
            decomposition = _decompose(bracket, basis, realizations)
            constants.extend(
                {
                    "X": left_label,
                    "Y": right_label,
                    "Z": output_label,
                    "coeff": str(coefficient),
                    "sign_rule": "graded",
                }
                for output_label, coefficient in decomposition.items()
            )
    return constants


def build_schema(n: int) -> dict[str, object]:
    if n < 1:
        raise ValueError("The bosonic rank n must be at least 1")
    basis, realizations, parity = _basis_realizations(n)
    order = _oscillator_order(n)
    realization_data = {}
    for label in basis:
        realization_data[label] = {
            "standard_form": _standard_form(realizations[label]),
            "frappat_form": _display_realization(label, n),
            "parity": parity[label],
        }
    even_count = 2 * n * n + n + 1
    odd_count = 4 * n
    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n + 1})",
            "alternative_notation": {
                "osp": f"osp(2|{2 * n})",
                "dimension_formula": "osp(2m|2n)",
            },
            "dimension": {
                "total": even_count + odd_count,
                "even": even_count,
                "odd": odd_count,
                "even_formula": "2n^2 + n + 1",
                "odd_formula": "4n",
                "total_formula": "2n^2 + 5n + 1",
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
                "description": "Bosonic oscillators b_k^+, b_k^- for k=1,...,n",
            },
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations",
                "relations": {
                    "same_type": "{a_1^+, a_1^+} = {a_1^-, a_1^-} = 0",
                    "conjugate_pair": "{a_1^-, a_1^+} = 1",
                },
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations for bosonic oscillators",
                "relations": {
                    "same_type": "[b_i^±, b_j^±] = 0 for all i,j",
                    "conjugate_pair": "[b_i^-, b_j^+] = δ_ij",
                },
            },
            "mixed_commutators": {
                "fermion_boson": "[a_1^σ, b_j^s] = 0 in the undeformed algebra",
            },
        },
        "central_elements": {
            "kappa": {
                "label": "κ",
                "parity": 1,
                "central": True,
                "nilpotent": True,
                "relation": "κ^2 = 0",
            },
            "K": {
                "label": "K",
                "parity": 0,
                "central": True,
                "identified_with": "1",
                "independent_basis_element": False,
            },
        },
        "basis": {
            "even": [label for label in basis if parity[label] == 0],
            "odd": [label for label in basis if parity[label] == 1],
            "ordering_convention": (
                "PBW: κ < negative roots < Cartan < positive roots; "
                "within each root block, even roots precede odd roots"
            ),
        },
        "parity": parity,
        "generator_realization": {
            "description": "Standard form with PBW-ordered oscillator words",
            "ordering": list(order),
            "realizations": realization_data,
        },
        "structure_constants": _structure_constants(
            basis, realizations, parity, order
        ),
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": date.today().isoformat(),
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "Bakalov and Sullivan (2017)",
            ],
        },
    }


def write_schema(n: int, output_dir: Path = DATA_DIR) -> Path:
    schema = build_schema(n)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"C_{n}_structure.json"
    output_path.write_text(
        json.dumps(schema, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ranks",
        type=int,
        nargs="+",
        default=[1, 2, 3],
        help="Bosonic ranks to generate (default: 1 2 3)",
    )
    parser.add_argument("--output-dir", type=Path, default=DATA_DIR)
    arguments = parser.parse_args()
    for rank in arguments.ranks:
        path = write_schema(rank, arguments.output_dir)
        print(path)


if __name__ == "__main__":
    main()
