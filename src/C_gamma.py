#!/usr/bin/env python3
"""Generate Schema 2 inhomogeneous deformation data for C(n+1)."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import date
from fractions import Fraction
from pathlib import Path

if __package__:
    from .C_generators import ROOT, _inverse, build_basis, build_realizations, oscillator_order
else:
    from C_generators import ROOT, _inverse, build_basis, build_realizations, oscillator_order

DATA_DIR = ROOT / "data"
SUFFIXES = ("pp", "pm", "mp", "mm")
Term = tuple[tuple[str, ...], tuple[str, ...], bool]
Polynomial = dict[Term, Fraction]


def _parameter(fermion: str, boson: str) -> str:
    return f"gb_a1_{fermion.rsplit('_', 1)[1]}_b{boson.split('_')[1]}_{boson.rsplit('_', 1)[1]}"


def _normal_order(
    word: tuple[str, ...],
    order: dict[str, int],
    parameters: tuple[str, ...] = (),
    has_kappa: bool = False,
) -> Polynomial:
    for i in range(len(word) - 1):
        left, right = word[i], word[i + 1]
        if left == right and left.startswith("a_1_"):
            return {}
        if order[left] <= order[right]:
            continue
        prefix, suffix = word[:i], word[i + 2 :]
        swapped = prefix + (right, left) + suffix
        fermion_swap = left.startswith("a_1_") and right.startswith("a_1_")
        sign = Fraction(-1 if fermion_swap else 1)
        result: defaultdict[Term, Fraction] = defaultdict(Fraction)
        for term, coeff in _normal_order(swapped, order, parameters, has_kappa).items():
            result[term] += sign * coeff

        contraction = (
            left == "a_1_m" and right == "a_1_p"
        ) or (
            left.startswith("b_") and right.startswith("b_")
            and left.endswith("_m") and right.endswith("_p")
            and left.split("_")[1] == right.split("_")[1]
        )
        if contraction:
            for term, coeff in _normal_order(
                prefix + suffix, order, parameters, has_kappa
            ).items():
                result[term] += coeff
        if left.startswith("b_") and right.startswith("a_1_") and not has_kappa:
            parameter = _parameter(right, left)
            new_parameters = tuple(sorted((*parameters, parameter)))
            for term, coeff in _normal_order(
                prefix + suffix, order, new_parameters, True
            ).items():
                result[term] -= coeff
        return {term: coeff for term, coeff in result.items() if coeff}
    return {(word, parameters, has_kappa): Fraction(1)}


def _multiply(
    left: dict[tuple[str, ...], Fraction],
    right: dict[tuple[str, ...], Fraction],
    order: dict[str, int],
) -> Polynomial:
    result: defaultdict[Term, Fraction] = defaultdict(Fraction)
    for x, cx in left.items():
        for y, cy in right.items():
            for term, coeff in _normal_order(x + y, order).items():
                result[term] += cx * cy * coeff
    return {term: coeff for term, coeff in result.items() if coeff}


def _add(left: Polynomial, right: Polynomial, factor: Fraction = Fraction(1)) -> Polynomial:
    result: defaultdict[Term, Fraction] = defaultdict(Fraction, left)
    for term, coeff in right.items():
        result[term] += factor * coeff
    return {term: coeff for term, coeff in result.items() if coeff}


def _basis_coordinates(
    n: int,
    labels: list[str],
    realizations: dict[str, dict[tuple[str, ...], Fraction]],
) -> tuple[list[tuple[str, ...]], list[int], list[list[Fraction]]]:
    order = dict(zip(oscillator_order(n), range(2 + 2 * n)))
    monomials = sorted(
        {word for label in labels for word in realizations[label]},
        key=lambda word: (len(word), tuple(order[token] for token in word)),
    )
    matrix = [
        [realizations[label].get(word, Fraction(0)) for label in labels]
        for word in monomials
    ]
    selected_rows: list[int] = []
    pivots: dict[int, list[Fraction]] = {}
    for row_index, original_row in enumerate(matrix):
        row = list(original_row)
        for pivot_index, pivot_row in sorted(pivots.items()):
            factor = row[pivot_index]
            if factor:
                row = [value - factor * pivot for value, pivot in zip(row, pivot_row)]
        pivot_index = next((i for i, value in enumerate(row) if value), None)
        if pivot_index is not None:
            divisor = row[pivot_index]
            pivots[pivot_index] = [value / divisor for value in row]
            selected_rows.append(row_index)
            if len(selected_rows) == len(labels):
                break
    if len(selected_rows) != len(labels):
        raise ValueError("Declared generator realizations are linearly dependent")
    square = [[matrix[row][column] for column in range(len(labels))] for row in selected_rows]
    inverse = _inverse(square)
    return monomials, selected_rows, [list(row) for row in inverse]


def _express_in_basis(
    word_coefficients: dict[tuple[str, ...], Fraction],
    labels: list[str],
    monomials: list[tuple[str, ...]],
    selected_rows: list[int],
    inverse: list[list[Fraction]],
    realizations: dict[str, dict[tuple[str, ...], Fraction]],
    context: str,
) -> dict[str, Fraction]:
    if any(word not in monomials for word in word_coefficients):
        raise ValueError("Gamma term contains oscillator words outside the C(n+1) basis span")
    selected_vector = [word_coefficients.get(monomials[row], Fraction(0)) for row in selected_rows]
    coefficients = [
        sum((inverse[i][j] * selected_vector[j] for j in range(len(labels))), Fraction(0))
        for i in range(len(labels))
    ]
    for word in monomials:
        expected = word_coefficients.get(word, Fraction(0))
        actual = sum(
            (
                realizations[label].get(word, Fraction(0)) * coefficient
                for label, coefficient in zip(labels, coefficients)
            ),
            Fraction(0),
        )
        if actual != expected:
            raise ValueError(
                f"Gamma term for {context} does not close at {word}: "
                f"expected {expected}, reconstructed {actual}"
            )
    return {label: coeff for label, coeff in zip(labels, coefficients) if coeff}


def _gamma_coefficients(n: int) -> list[dict[str, object]]:
    even, odd = build_basis(n)
    labels = even + odd
    realizations, _ = build_realizations(n)
    target_labels = labels + ["K"]
    target_realizations = dict(realizations)
    target_realizations["K"] = {(): Fraction(1)}
    monomials, selected_rows, inverse = _basis_coordinates(n, target_labels, target_realizations)
    order = dict(zip(oscillator_order(n), range(2 + 2 * n)))
    parities = {label: int(label in odd) for label in labels}
    coefficients: list[dict[str, object]] = []

    for x_index, x in enumerate(labels):
        for y in labels[x_index:]:
            sign = -1 if parities[x] * parities[y] else 1
            bracket = _add(
                _multiply(realizations[x], realizations[y], order),
                _multiply(realizations[y], realizations[x], order),
                Fraction(-sign),
            )
            gamma_words: defaultdict[str, dict[tuple[str, ...], Fraction]] = defaultdict(
                lambda: defaultdict(Fraction)
            )
            for (word, parameters, has_kappa), coeff in bracket.items():
                if has_kappa:
                    if len(parameters) != 1:
                        raise ValueError("Expected a first-order term with exactly one gb parameter")
                    gamma_words[parameters[0]][word] += coeff

            by_output: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
            for parameter, words in gamma_words.items():
                expressed = _express_in_basis(
                    dict(words), target_labels, monomials, selected_rows, inverse, target_realizations,
                    f"[{x}, {y}] parameter {parameter}",
                )
                for z, coeff in expressed.items():
                    by_output[z].append({"parameter": parameter, "coeff": str(coeff)})
            for z, terms in by_output.items():
                coefficients.append({
                    "X": x,
                    "Y": y,
                    "Z": z,
                    "coefficients": sorted(terms, key=lambda term: term["parameter"]),
                })
    return coefficients


def build_gamma_schema(n: int, structure_path: Path | None = None) -> dict[str, object]:
    if n < 1:
        raise ValueError("n must be at least 1")
    source_path = structure_path or DATA_DIR / f"C_{n}_structure.json"
    with source_path.open(encoding="utf-8") as stream:
        structure = json.load(stream)
    even, odd = build_basis(n)
    labels = even + odd
    if structure["algebra"]["family"] != "C" or structure["algebra"]["n"] != n:
        raise ValueError(f"{source_path} does not match C-family rank {n}")
    if structure["basis"]["even"] != even or structure["basis"]["odd"] != odd:
        raise ValueError(f"{source_path} basis does not match the Schema 1 basis")
    if structure["parity"] != {label: int(label in odd) for label in labels}:
        raise ValueError(f"{source_path} parity does not match the Schema 1 basis")

    fermions = ("a_1_p", "a_1_m")
    bosons = structure["oscillator_generators"]["bosons"]["labels"]
    parameters = [[_parameter(fermion, boson) for boson in bosons] for fermion in fermions]
    return {
        "schema_version": "5.0",
        "algebra": structure["algebra"],
        "source_schema": source_path.name,
        "gb_matrix": {
            "rows": list(fermions),
            "columns": bosons,
            "shape": [2, 2 * n],
            "parameters": parameters,
            "parameter_parity": 1,
        },
        "inhomogeneous_deformation": {
            "relations": [
                {
                    "boson": boson,
                    "fermion": fermion,
                    "parameter": _parameter(fermion, boson),
                    "relation": f"[{boson}, {fermion}] = -{_parameter(fermion, boson)} κ",
                }
                for fermion in fermions
                for boson in bosons
            ],
            "gamma_convention": (
                "Deformed graded bracket = undeformed bracket + κ times gamma; "
                "gamma coefficients are listed once for each canonical basis pair."
            ),
            "formal_coefficient_convention": (
                "gb parameters are retained as formal labels. The source assigns odd parity "
                "to both gb and κ, although their product is even while the mixed oscillator "
                "bracket is odd; no parity sign is inferred from the formal coefficient."
            ),
            "central_targets": ["K"],
            "gamma_coefficients": _gamma_coefficients(n),
        },
        "metadata": {
            "generated_by": "src/C_gamma.py",
            "generation_date": date.today().isoformat(),
            "references": [
                "docs/math/C_inhomogeneous_definition.md",
                "docs/json_schema_specification.md",
            ],
        },
    }


def generate(n: int, output_dir: Path = DATA_DIR) -> Path:
    schema = build_gamma_schema(n)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"C_{n}_gamma.json"
    path.write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, nargs="+", default=[1, 2, 3])
    parser.add_argument("--output-dir", type=Path, default=DATA_DIR)
    args = parser.parse_args()
    for rank in args.n:
        print(generate(rank, args.output_dir))


if __name__ == "__main__":
    main()
