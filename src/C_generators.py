"""Generate Schema 1 structure data for C(n+1) = osp(2|2n)."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from typing import TypeAlias


Word: TypeAlias = tuple[str, ...]
Polynomial: TypeAlias = dict[Word, Fraction]


def _generator_order(n: int) -> dict[str, int]:
    labels = ["a_1_p", "a_1_m"]
    labels.extend(f"b_{i}_p" for i in range(1, n + 1))
    labels.extend(f"b_{i}_m" for i in range(1, n + 1))
    return {label: index for index, label in enumerate(labels)}


def _normalize_word(word: Word, n: int) -> Polynomial:
    """Rewrite an oscillator word to fermion/boson creation-first order."""
    order = _generator_order(n)
    for index in range(len(word) - 1):
        left, right = word[index : index + 2]
        if left == right and left in ("a_1_p", "a_1_m"):
            return {}
        if order[left] <= order[right]:
            continue

        prefix, suffix = word[:index], word[index + 2 :]
        if left == "a_1_m" and right == "a_1_p":
            contracted = _normalize_word(prefix + suffix, n)
            swapped = _normalize_word(prefix + (right, left) + suffix, n)
            return _add_polynomials(contracted, swapped, Fraction(1), Fraction(-1))

        if left.startswith("b_") and left.endswith("_m") and right.startswith("b_") and right.endswith("_p"):
            left_mode = int(left.split("_")[1])
            right_mode = int(right.split("_")[1])
            contracted = _normalize_word(prefix + suffix, n) if left_mode == right_mode else {}
            swapped = _normalize_word(prefix + (right, left) + suffix, n)
            return _add_polynomials(contracted, swapped, Fraction(1), Fraction(1))

        return _normalize_word(prefix + (right, left) + suffix, n)

    return {word: Fraction(1)}


def _add_polynomials(
    left: Polynomial,
    right: Polynomial,
    left_scale: Fraction = Fraction(1),
    right_scale: Fraction = Fraction(1),
) -> Polynomial:
    result: Polynomial = {}
    for word, coeff in left.items():
        result[word] = result.get(word, Fraction(0)) + left_scale * coeff
    for word, coeff in right.items():
        result[word] = result.get(word, Fraction(0)) + right_scale * coeff
    return {word: coeff for word, coeff in result.items() if coeff}


def _scale_polynomial(poly: Polynomial, coeff: Fraction) -> Polynomial:
    return {word: value * coeff for word, value in poly.items() if value * coeff}


def _multiply(left: Polynomial, right: Polynomial, n: int) -> Polynomial:
    result: Polynomial = {}
    for left_word, left_coeff in left.items():
        for right_word, right_coeff in right.items():
            normalized = _normalize_word(left_word + right_word, n)
            result = _add_polynomials(
                result,
                _scale_polynomial(normalized, left_coeff * right_coeff),
            )
    return result


def _monomial(
    words: tuple[str, ...], n: int, coeff: Fraction = Fraction(1)
) -> Polynomial:
    return _scale_polynomial(_normalize_word(words, n), coeff)


def build_generators(n: int) -> tuple[list[str], list[str], dict[str, Polynomial], dict[str, int]]:
    if n < 1:
        raise ValueError("The bosonic rank n must be positive.")

    even: list[str] = [f"H_{i}" for i in range(1, n + 2)]
    even.extend(f"E_2del{i}_p" for i in range(1, n + 1))
    for i, j in combinations(range(1, n + 1), 2):
        even.extend(f"E_del{i}_del{j}_{suffix}" for suffix in ("pp", "pm", "mp", "mm"))
    even.extend(f"E_2del{i}_m" for i in range(1, n + 1))
    odd = [
        f"E_eps1_del{k}_{suffix}"
        for k in range(1, n + 1)
        for suffix in ("pp", "pm", "mp", "mm")
    ]

    realizations: dict[str, Polynomial] = {}
    parity = {label: 0 for label in even}
    parity.update({label: 1 for label in odd})

    def boson_number(i: int) -> Word:
        return (f"b_{i}_p", f"b_{i}_m")

    realizations["H_1"] = _monomial(("a_1_p", "a_1_m"), n)
    realizations["H_1"] = _add_polynomials(
        realizations["H_1"], _monomial(boson_number(1), n)
    )
    for i in range(2, n + 1):
        realizations[f"H_{i}"] = _add_polynomials(
            _monomial(boson_number(i - 1), n),
            _monomial(boson_number(i), n, Fraction(-1)),
        )
    realizations[f"H_{n + 1}"] = _add_polynomials(
        _monomial(boson_number(n), n, Fraction(-1)),
        _monomial((), n, Fraction(-1, 2)),
    )

    for i in range(1, n + 1):
        realizations[f"E_2del{i}_p"] = _monomial((f"b_{i}_p", f"b_{i}_p"), n)
        realizations[f"E_2del{i}_m"] = _monomial((f"b_{i}_m", f"b_{i}_m"), n)
    for i, j in combinations(range(1, n + 1), 2):
        for suffix, signs in {
            "pp": ("p", "p"),
            "pm": ("p", "m"),
            "mp": ("m", "p"),
            "mm": ("m", "m"),
        }.items():
            realizations[f"E_del{i}_del{j}_{suffix}"] = _monomial(
                (f"b_{i}_{signs[0]}", f"b_{j}_{signs[1]}"), n
            )

    for k in range(1, n + 1):
        for suffix, signs in {
            "pp": ("p", "p"),
            "pm": ("p", "m"),
            "mp": ("m", "p"),
            "mm": ("m", "m"),
        }.items():
            realizations[f"E_eps1_del{k}_{suffix}"] = _monomial(
                (f"a_1_{signs[0]}", f"b_{k}_{signs[1]}"), n
            )
    return even, odd, realizations, parity


def _bracket(x: Polynomial, y: Polynomial, px: int, py: int, n: int) -> Polynomial:
    xy = _multiply(x, y, n)
    yx = _multiply(y, x, n)
    return _add_polynomials(xy, yx, Fraction(1), Fraction(-1 if not (px and py) else 1))


def _linear_coordinates(
    basis: list[Polynomial], vector: Polynomial
) -> list[Fraction]:
    monomials = sorted(
        {word for poly in basis for word in poly} | set(vector),
        key=lambda word: (len(word), word),
    )
    matrix = [
        [poly.get(word, Fraction(0)) for poly in basis] + [vector.get(word, Fraction(0))]
        for word in monomials
    ]
    pivot_rows: dict[int, int] = {}
    row = 0
    for column in range(len(basis)):
        pivot = next(
            (candidate for candidate in range(row, len(matrix)) if matrix[candidate][column]),
            None,
        )
        if pivot is None:
            raise ValueError("The generator realizations are linearly dependent.")
        matrix[row], matrix[pivot] = matrix[pivot], matrix[row]
        pivot_value = matrix[row][column]
        matrix[row] = [value / pivot_value for value in matrix[row]]
        for other in range(len(matrix)):
            if other != row and matrix[other][column]:
                factor = matrix[other][column]
                matrix[other] = [
                    value - factor * pivot_value
                    for value, pivot_value in zip(matrix[other], matrix[row])
                ]
        pivot_rows[column] = row
        row += 1

    for equation in matrix:
        if not any(equation[:-1]) and equation[-1]:
            raise ValueError("An oscillator bracket is outside the proposed basis.")
    return [matrix[pivot_rows[column]][-1] for column in range(len(basis))]


def _oscillator_words(poly: Polynomial) -> list[dict[str, object]]:
    return [
        {"words": list(word), "coeff": str(coeff)}
        for word, coeff in sorted(poly.items(), key=lambda item: (len(item[0]), item[0]))
    ]


def _frappat_form(poly: Polynomial) -> str:
    names = {
        "a_1_p": "a_1^+",
        "a_1_m": "a_1^-",
    }
    terms = []
    for word, coeff in sorted(poly.items(), key=lambda item: (len(item[0]), item[0])):
        factors = [
            names.get(label, label.replace("_p", "^+").replace("_m", "^-"))
            for label in word
        ]
        monomial = " ".join(factors) if factors else "1"
        if not word:
            term = str(coeff)
        elif coeff == 1:
            term = monomial
        elif coeff == -1:
            term = f"-{monomial}"
        else:
            term = f"{coeff} {monomial}"
        terms.append(term)
    result = " + ".join(terms).replace("+ -", "- ")
    return result or "0"


def build_schema(n: int, generation_date: str = "2026-10-04") -> dict[str, object]:
    even, odd, realizations, parity = build_generators(n)
    pbw_labels = odd + even
    basis_polynomials = [realizations[label] for label in pbw_labels]
    brackets: list[dict[str, str]] = []
    for i, x_label in enumerate(pbw_labels):
        for j in range(i, len(pbw_labels)):
            y_label = pbw_labels[j]
            result = _bracket(
                realizations[x_label], realizations[y_label],
                parity[x_label], parity[y_label], n,
            )
            if not result:
                continue
            coefficients = _linear_coordinates(basis_polynomials, result)
            for z_label, coeff in zip(pbw_labels, coefficients):
                if coeff:
                    brackets.append({
                        "X": x_label,
                        "Y": y_label,
                        "Z": z_label,
                        "coeff": str(coeff),
                        "sign_rule": "graded",
                    })

    realization_data = {}
    for label in pbw_labels:
        realization_data[label] = {
            "standard_form": _oscillator_words(realizations[label]),
            "frappat_form": _frappat_form(realizations[label]),
            "parity": parity[label],
        }
    bosons = [
        label
        for i in range(1, n + 1)
        for label in (f"b_{i}_p", f"b_{i}_m")
    ]
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
                "description": "One standard fermionic creation/annihilation pair.",
            },
            "bosons": {
                "n": n,
                "count": 2 * n,
                "labels": bosons,
                "parity": 0,
                "description": f"Bosonic creation/annihilation pairs for i=1,...,{n}.",
            },
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations for the standard pair.",
                "relations": {
                    "conjugate_pair": "{a_1_m, a_1_p} = 1",
                    "same_type": "{a_1_p, a_1_p} = {a_1_m, a_1_m} = 0",
                },
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations for bosonic oscillators.",
                "relations": {
                    "same_type": "[b_i_s, b_j_t] = 0",
                    "conjugate_pair": "[b_i_m, b_j_p] = δ_ij",
                },
            },
            "mixed_commutators": {"fermion_boson": "[a_1_s, b_i_t] = 0"},
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
            "ordering_convention": (
                "PBW: κ < [odd generators] < [even generators]; K = 1 is excluded."
            ),
        },
        "parity": parity,
        "generator_realization": {
            "description": "Standard form with PBW ordering.",
            "ordering": ["a_1_p", "a_1_m"] + bosons,
            "realizations": realization_data,
        },
        "structure_constants": brackets,
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": generation_date,
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "docs/math/Cn1_definition.md",
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
        output = args.output_dir / f"C_{n}_structure.json"
        output.write_text(
            json.dumps(build_schema(n), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"Wrote {output}")


if __name__ == "__main__":
    main()
