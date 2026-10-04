"""Generate Schema 1 structure data for C(n+1) = osp(2|2n)."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import date
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Iterable

Word = tuple[str, ...]
Polynomial = dict[Word, Fraction]


def _token_order(token: str) -> tuple[int, int]:
    if token == "a_1_p":
        return (0, 0)
    if token == "a_1_m":
        return (0, 1)
    _, index, sign = token.split("_")
    return (int(index), 0 if sign == "p" else 1)


def _fermion(token: str) -> bool:
    return token.startswith("a_")


def _is_annihilator_creator_pair(left: str, right: str) -> bool:
    return (
        (left == "a_1_m" and right == "a_1_p")
        or (
            left.startswith("b_")
            and right.startswith("b_")
            and left.split("_")[1] == right.split("_")[1]
            and left.endswith("_m")
            and right.endswith("_p")
        )
    )


@lru_cache(maxsize=None)
def _normal_order_word(word: Word) -> tuple[tuple[Word, Fraction], ...]:
    for index in range(len(word) - 1):
        left, right = word[index], word[index + 1]
        prefix, suffix = word[:index], word[index + 2 :]

        if _fermion(left) and left == right:
            return ()

        if _token_order(left) <= _token_order(right):
            continue

        swapped = prefix + (right, left) + suffix
        if _is_annihilator_creator_pair(left, right):
            scalar = _normal_order_word(prefix + suffix)
            ordered = _normal_order_word(swapped)
            result: defaultdict[Word, Fraction] = defaultdict(Fraction)
            for term, coeff in scalar:
                result[term] += coeff
            swap_sign = Fraction(-1) if _fermion(left) else Fraction(1)
            for term, coeff in ordered:
                result[term] += swap_sign * coeff
            return tuple((term, coeff) for term, coeff in result.items() if coeff)

        return _normal_order_word(swapped)

    return ((word, Fraction(1)),)


def _polynomial(terms: Iterable[tuple[Word, Fraction | int]]) -> Polynomial:
    result: defaultdict[Word, Fraction] = defaultdict(Fraction)
    for word, coefficient in terms:
        for normal_word, factor in _normal_order_word(tuple(word)):
            result[normal_word] += Fraction(coefficient) * factor
    return {word: coeff for word, coeff in result.items() if coeff}


def _add(left: Polynomial, right: Polynomial, scale: Fraction = Fraction(1)) -> Polynomial:
    result = defaultdict(Fraction, left)
    for word, coefficient in right.items():
        result[word] += scale * coefficient
    return {word: coeff for word, coeff in result.items() if coeff}


def _multiply(left: Polynomial, right: Polynomial) -> Polynomial:
    terms = []
    for left_word, left_coeff in left.items():
        for right_word, right_coeff in right.items():
            terms.append((left_word + right_word, left_coeff * right_coeff))
    return _polynomial(terms)


def _superbracket(
    left: Polynomial,
    right: Polynomial,
    left_parity: int,
    right_parity: int,
) -> Polynomial:
    sign = -1 if left_parity * right_parity % 2 else 1
    return _add(_multiply(left, right), _multiply(right, left), Fraction(-sign))


def _generator_data(n: int) -> tuple[list[str], dict[str, int], dict[str, Polynomial]]:
    if n < 1:
        raise ValueError("bosonic rank n must be at least 1")

    realizations: dict[str, Polynomial] = {}
    parity: dict[str, int] = {}

    def add(label: str, terms: Iterable[tuple[Word, Fraction | int]], p: int) -> None:
        realizations[label] = _polynomial(terms)
        parity[label] = p

    add("H_1", [(("a_1_p", "a_1_m"), 1), (("b_1_p", "b_1_m"), 1)], 0)
    for k in range(2, n + 1):
        add(
            f"H_{k}",
            [
                ((f"b_{k - 1}_p", f"b_{k - 1}_m"), 1),
                ((f"b_{k}_p", f"b_{k}_m"), -1),
            ],
            0,
        )
    add(
        f"H_{n + 1}",
        [((f"b_{n}_p", f"b_{n}_m"), -1), ((), Fraction(-1, 2))],
        0,
    )

    for k in range(1, n + 1):
        add(f"E_2del{k}_m", [((f"b_{k}_m", f"b_{k}_m"), 1)], 0)
        add(f"E_2del{k}_p", [((f"b_{k}_p", f"b_{k}_p"), 1)], 0)

    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            for suffix, signs in (
                ("mp", ("m", "p")),
                ("mm", ("m", "m")),
                ("pm", ("p", "m")),
                ("pp", ("p", "p")),
            ):
                add(
                    f"E_del{i}_del{j}_{suffix}",
                    [((f"b_{i}_{signs[0]}", f"b_{j}_{signs[1]}"), 1)],
                    0,
                )

    for k in range(1, n + 1):
        for suffix, fermion_sign, boson_sign in (
            ("mp", "m", "p"),
            ("mm", "m", "m"),
            ("pm", "p", "m"),
            ("pp", "p", "p"),
        ):
            add(
                f"E_eps1_del{k}_{suffix}",
                [((f"a_1_{fermion_sign}", f"b_{k}_{boson_sign}"), 1)],
                1,
            )

    negative_odd = [
        f"E_eps1_del{k}_{suffix}"
        for k in range(1, n + 1)
        for suffix in ("mp", "mm")
    ]
    negative_even = [
        f"E_del{i}_del{j}_{suffix}"
        for i in range(1, n + 1)
        for j in range(i + 1, n + 1)
        for suffix in ("mp", "mm")
    ] + [f"E_2del{k}_m" for k in range(1, n + 1)]
    cartan = [f"H_{k}" for k in range(1, n + 2)]
    positive_even = [
        f"E_del{i}_del{j}_{suffix}"
        for i in range(1, n + 1)
        for j in range(i + 1, n + 1)
        for suffix in ("pm", "pp")
    ] + [f"E_2del{k}_p" for k in range(1, n + 1)]
    positive_odd = [
        f"E_eps1_del{k}_{suffix}"
        for k in range(1, n + 1)
        for suffix in ("pm", "pp")
    ]
    full_order = negative_odd + negative_even + cartan + positive_even + positive_odd
    return full_order, parity, realizations


def _solve_coordinates(
    basis: list[str],
    realizations: dict[str, Polynomial],
    target: Polynomial,
) -> dict[str, Fraction]:
    monomials = sorted(
        set(target).union(*(realizations[label] for label in basis)),
        key=lambda word: (len(word), word),
    )
    matrix = [
        [realizations[label].get(word, Fraction()) for label in basis]
        + [target.get(word, Fraction())]
        for word in monomials
    ]

    pivot_row = 0
    pivot_rows: dict[int, int] = {}
    for column in range(len(basis)):
        pivot = next(
            (row for row in range(pivot_row, len(matrix)) if matrix[row][column]),
            None,
        )
        if pivot is None:
            raise ValueError(f"generator basis is linearly dependent at {basis[column]}")
        matrix[pivot_row], matrix[pivot] = matrix[pivot], matrix[pivot_row]
        scale = matrix[pivot_row][column]
        matrix[pivot_row] = [value / scale for value in matrix[pivot_row]]
        for row in range(len(matrix)):
            if row == pivot_row or not matrix[row][column]:
                continue
            factor = matrix[row][column]
            matrix[row] = [
                value - factor * pivot_value
                for value, pivot_value in zip(matrix[row], matrix[pivot_row])
            ]
        pivot_rows[column] = pivot_row
        pivot_row += 1

    for row in matrix:
        if not any(row[:-1]) and row[-1]:
            raise ValueError(f"bracket is outside the generator span: {target}")

    return {
        label: matrix[pivot_rows[column]][-1]
        for column, label in enumerate(basis)
        if matrix[pivot_rows[column]][-1]
    }


def _realization_json(polynomial: Polynomial, parity: int, n: int) -> dict:
    def readable_word(word: Word) -> str:
        mapping = {
            "a_1_p": "a_1^+",
            "a_1_m": "a_1^-",
        }
        for k in range(1, n + 1):
            mapping[f"b_{k}_p"] = f"b_{k}^+"
            mapping[f"b_{k}_m"] = f"b_{k}^-"
        return " ".join(mapping[token] for token in word) if word else "1"

    standard_form = [
        {"words": list(word), "coeff": str(coefficient)}
        for word, coefficient in sorted(polynomial.items(), key=lambda item: (len(item[0]), item[0]))
    ]
    expression = " + ".join(
        f"{coefficient} {readable_word(word)}"
        for word, coefficient in sorted(polynomial.items(), key=lambda item: (len(item[0]), item[0]))
    ).replace("+ -", "- ")
    return {
        "standard_form": standard_form,
        "frappat_form": expression,
        "parity": parity,
    }


def build_schema(n: int) -> dict:
    full_order, parity, realizations = _generator_data(n)
    even = [label for label in full_order if parity[label] == 0]
    odd = [label for label in full_order if parity[label] == 1]

    constants = []
    for i, left_label in enumerate(full_order):
        for right_label in full_order[i:]:
            bracket = _superbracket(
                realizations[left_label],
                realizations[right_label],
                parity[left_label],
                parity[right_label],
            )
            coordinates = _solve_coordinates(full_order, realizations, bracket) if bracket else {}
            for result_label, coefficient in coordinates.items():
                constants.append(
                    {
                        "X": left_label,
                        "Y": right_label,
                        "Z": result_label,
                        "coeff": str(coefficient),
                        "sign_rule": "graded",
                    }
                )

    oscillator_labels = [
        label
        for k in range(1, n + 1)
        for label in (f"b_{k}_p", f"b_{k}_m")
    ]
    realization_map = {
        label: _realization_json(realizations[label], parity[label], n)
        for label in full_order
    }
    for k in range(1, n + 1):
        realization_map[f"H_{k}"]["frappat_form"] = (
            "a_1^+ a_1^- + b_1^+ b_1^-"
            if k == 1
            else f"b_{k - 1}^+ b_{k - 1}^- - b_{k}^+ b_{k}^-"
        )
    realization_map[f"H_{n + 1}"]["frappat_form"] = (
        f"-b_{n}^+ b_{n}^- - 1/2"
    )
    for k in range(1, n + 1):
        realization_map[f"E_2del{k}_m"]["frappat_form"] = f"(b_{k}^-)^2"
        realization_map[f"E_2del{k}_p"]["frappat_form"] = f"(b_{k}^+)^2"
    for label in full_order:
        if label.startswith("E_del"):
            _, first, second, suffix = label.split("_")
            i, j = first.removeprefix("del"), second.removeprefix("del")
            signs = {"p": "+", "m": "-"}
            realization_map[label]["frappat_form"] = (
                f"b_{i}^{signs[suffix[0]]} b_{j}^{signs[suffix[1]]}"
            )
        elif label.startswith("E_eps1_del"):
            _, _, del_index, suffix = label.split("_")
            k = del_index.removeprefix("del")
            signs = {"p": "+", "m": "-"}
            realization_map[label]["frappat_form"] = (
                f"a_1^{signs[suffix[0]]} b_{k}^{signs[suffix[1]]}"
            )

    even_dimension = 2 * n * n + n + 1
    odd_dimension = 4 * n
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
                "total": even_dimension + odd_dimension,
                "even": even_dimension,
                "odd": odd_dimension,
                "even_formula": "2n^2 + n + 1",
                "odd_formula": "4n",
                "total_formula": "2n^2 + 5n + 1",
            },
        },
        "oscillator_generators": {
            "fermions": {
                "m": 1,
                "labels": ["a_1_p", "a_1_m"],
                "parity": 1,
                "description": "Standard fermionic pair a_1^+, a_1^-",
            },
            "bosons": {
                "n": n,
                "count": 2 * n,
                "labels": oscillator_labels,
                "parity": 0,
                "description": "Bosonic oscillator pairs b_k^+, b_k^- for k=1,...,n",
            },
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations for a_1^-, a_1^+",
                "relations": {
                    "conjugate_pair": "{a_1_m, a_1_p} = 1",
                    "same_type": "{a_1_p, a_1_p} = {a_1_m, a_1_m} = 0",
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
                "fermion_boson": "[a_1^±, b_j^±] = 0 for all j"
            },
        },
        "central_elements": {
            "kappa": {
                "label": "kappa",
                "parity": 1,
                "relation": "kappa^2 = 0",
                "central": True,
                "description": "Odd formal symbol for the nilpotent extension",
            },
            "K": {
                "label": "K",
                "parity": 0,
                "relation": "K = 1",
                "central": True,
                "description": "Even central identity; identified with the scalar 1",
            },
        },
        "basis": {
            "even": even,
            "odd": odd,
            "ordering_convention": (
                "PBW: negative roots < Cartan < positive roots; "
                "see handover/notation.md"
            ),
        },
        "parity": parity,
        "generator_realization": {
            "description": (
                "All-root realization with E_±2δ_k=(b_k^±)^2; "
                "standard form uses creation-before-annihilation ordering"
            ),
            "ordering": ", ".join(["a_1_p", "a_1_m", *oscillator_labels]),
            "realizations": realization_map,
        },
        "structure_constants": constants,
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": date.today().isoformat(),
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "docs/math/Cn1_definition.md",
                "docs/math/B0n_schema_v5.md",
            ],
        },
    }


def generate(output_directory: Path, ranks: Iterable[int] = (1, 2, 3)) -> list[Path]:
    output_directory.mkdir(parents=True, exist_ok=True)
    generated = []
    for n in ranks:
        schema = build_schema(n)
        path = output_directory / f"C_{n}_structure.json"
        path.write_text(
            json.dumps(schema, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        generated.append(path)
    return generated


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data",
    )
    parser.add_argument("--ranks", type=int, nargs="+", default=[1, 2, 3])
    args = parser.parse_args()
    for path in generate(args.output_dir, args.ranks):
        print(path)


if __name__ == "__main__":
    main()
