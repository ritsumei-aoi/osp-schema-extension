#!/usr/bin/env python3
"""Generate Schema 1 basis and structure constants for C(n+1)."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import date
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
SUFFIXES = ("pp", "pm", "mp", "mm")


def oscillator_order(n: int) -> tuple[str, ...]:
    return ("a_1_p", "a_1_m", *(
        label for i in range(1, n + 1) for label in (f"b_{i}_p", f"b_{i}_m")
    ))


def _normal_order_word(word: tuple[str, ...], order: dict[str, int]) -> dict[tuple[str, ...], Fraction]:
    for i in range(len(word) - 1):
        left, right = word[i], word[i + 1]
        left_rank, right_rank = order[left], order[right]
        if left == right and left.startswith("a_1_"):
            return {}
        if left_rank <= right_rank:
            continue

        prefix, suffix = word[:i], word[i + 2 :]
        swapped = prefix + (right, left) + suffix
        is_fermion_pair = left.startswith("a_1_") and right.startswith("a_1_")
        sign = -1 if is_fermion_pair else 1
        result = {
            monomial: sign * coeff
            for monomial, coeff in _normal_order_word(swapped, order).items()
        }
        contraction = (
            left == "a_1_m" and right == "a_1_p"
        ) or (
            left.startswith("b_") and right.startswith("b_")
            and left.endswith("_m") and right.endswith("_p")
            and left.split("_")[1] == right.split("_")[1]
        )
        if contraction:
            for monomial, coeff in _normal_order_word(prefix + suffix, order).items():
                result[monomial] = result.get(monomial, Fraction(0)) + coeff
        return {monomial: coeff for monomial, coeff in result.items() if coeff}
    return {word: Fraction(1)}


def _multiply(
    left: dict[tuple[str, ...], Fraction],
    right: dict[tuple[str, ...], Fraction],
    order: dict[str, int],
) -> dict[tuple[str, ...], Fraction]:
    result: defaultdict[tuple[str, ...], Fraction] = defaultdict(lambda: Fraction(0))
    for x, cx in left.items():
        for y, cy in right.items():
            for monomial, coeff in _normal_order_word(x + y, order).items():
                result[monomial] += cx * cy * coeff
    return {monomial: coeff for monomial, coeff in result.items() if coeff}


def _add(
    left: dict[tuple[str, ...], Fraction],
    right: dict[tuple[str, ...], Fraction],
    factor: Fraction = Fraction(1),
) -> dict[tuple[str, ...], Fraction]:
    result = defaultdict(lambda: Fraction(0), left)
    for monomial, coeff in right.items():
        result[monomial] += factor * coeff
    return {monomial: coeff for monomial, coeff in result.items() if coeff}


def build_basis(n: int) -> tuple[list[str], list[str]]:
    if n < 1:
        raise ValueError("n must be at least 1")
    even = [f"H_{i}" for i in range(1, n + 2)]
    even.extend(label for i in range(1, n + 1) for label in (f"E_2del{i}_p", f"E_2del{i}_m"))
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even.extend(f"E_del{i}_del{j}_{suffix}" for suffix in SUFFIXES)
    odd = [
        f"E_eps1_del{i}_{suffix}"
        for i in range(1, n + 1)
        for suffix in SUFFIXES
    ]
    return even, odd


def build_realizations(n: int) -> tuple[dict[str, dict[tuple[str, ...], Fraction]], dict[str, str]]:
    order = dict(zip(oscillator_order(n), range(2 + 2 * n)))
    realizations: dict[str, dict[tuple[str, ...], Fraction]] = {}
    forms: dict[str, str] = {}

    def add(label: str, terms: list[tuple[tuple[str, ...], Fraction]], form: str) -> None:
        polynomial: dict[tuple[str, ...], Fraction] = {}
        for letters, coeff in terms:
            polynomial = _add(polynomial, _normal_order_word(letters, order), coeff)
        realizations[label] = polynomial
        forms[label] = form

    add(
        "H_1",
        [(("a_1_p", "a_1_m"), Fraction(1)), (("b_1_p", "b_1_m"), Fraction(1))],
        "a_1^+ a_1^- + b_1^+ b_1^-",
    )
    for i in range(2, n + 1):
        add(
            f"H_{i}",
            [
                ((f"b_{i - 1}_p", f"b_{i - 1}_m"), Fraction(1)),
                ((f"b_{i}_p", f"b_{i}_m"), Fraction(-1)),
            ],
            f"b_{i - 1}^+ b_{i - 1}^- - b_{i}^+ b_{i}^-",
        )
    add(
        f"H_{n + 1}",
        [
            ((f"b_{n}_p", f"b_{n}_m"), Fraction(-1)),
            ((), Fraction(-1, 2)),
        ],
        f"-b_{n}^+ b_{n}^- - 1/2",
    )

    for i in range(1, n + 1):
        add(f"E_2del{i}_p", [((f"b_{i}_p", f"b_{i}_p"), Fraction(1))], f"(b_{i}^+)^2")
        add(f"E_2del{i}_m", [((f"b_{i}_m", f"b_{i}_m"), Fraction(1))], f"(b_{i}^-)^2")
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            for suffix, first, second, signs in (
                ("pp", "p", "p", ("+", "+")),
                ("pm", "p", "m", ("+", "-")),
                ("mp", "m", "p", ("-", "+")),
                ("mm", "m", "m", ("-", "-")),
            ):
                label = f"E_del{i}_del{j}_{suffix}"
                add(
                    label,
                    [((f"b_{i}_{first}", f"b_{j}_{second}"), Fraction(1))],
                    f"b_{i}^{signs[0]} b_{j}^{signs[1]}",
                )

    odd_forms = {
        "pp": ("p", "p", "+", "+"),
        "pm": ("p", "m", "+", "-"),
        "mp": ("m", "p", "-", "+"),
        "mm": ("m", "m", "-", "-"),
    }
    for i in range(1, n + 1):
        for suffix, (fermion, boson, epsilon_sign, delta_sign) in odd_forms.items():
            label = f"E_eps1_del{i}_{suffix}"
            add(
                label,
                [((f"a_1_{fermion}", f"b_{i}_{boson}"), Fraction(1))],
                f"a_1^{epsilon_sign} b_{i}^{delta_sign}",
            )
    return realizations, forms


def _format_rational(value: Fraction) -> str:
    return str(value)


def _standard_form(polynomial: dict[tuple[str, ...], Fraction]) -> list[dict[str, object]]:
    return [
        {"words": list(word), "coeff": _format_rational(coeff)}
        for word, coeff in sorted(polynomial.items(), key=lambda item: (len(item[0]), item[0]))
        if coeff
    ]


def _structure_constants(
    even: list[str],
    odd: list[str],
    realizations: dict[str, dict[tuple[str, ...], Fraction]],
    n: int,
) -> list[dict[str, str]]:
    labels = even + odd
    parities = {label: int(label.startswith("E_eps1_")) for label in labels}
    order = dict(zip(oscillator_order(n), range(2 + 2 * n)))
    monomials = sorted(
        {monomial for label in labels for monomial in realizations[label]},
        key=lambda monomial: (len(monomial), tuple(order[token] for token in monomial)),
    )
    matrix = [
        [realizations[label].get(monomial, Fraction(0)) for label in labels]
        for monomial in monomials
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
    constants: list[dict[str, str]] = []

    for x_index, x in enumerate(labels):
        for y in labels[x_index:]:
            sign = -1 if parities[x] * parities[y] else 1
            bracket = _add(
                _multiply(realizations[x], realizations[y], order),
                _multiply(realizations[y], realizations[x], order),
                Fraction(-sign),
            )
            if not bracket:
                continue
            if any(monomial not in monomials for monomial in bracket):
                raise ValueError(f"Bracket [{x}, {y}] has oscillator words outside the basis span")
            selected_vector = [bracket.get(monomials[row], Fraction(0)) for row in selected_rows]
            coefficients = [
                sum((inverse[i][j] * selected_vector[j] for j in range(len(labels))), Fraction(0))
                for i in range(len(labels))
            ]
            if any(
                sum((matrix[row][column] * coefficients[column] for column in range(len(labels))), Fraction(0))
                != bracket.get(monomial, Fraction(0))
                for row, monomial in enumerate(monomials)
            ):
                raise ValueError(f"Bracket [{x}, {y}] is not closed in the declared basis")
            for z, coefficient in zip(labels, coefficients):
                if coefficient:
                    constants.append({
                        "X": x,
                        "Y": y,
                        "Z": z,
                        "coeff": _format_rational(coefficient),
                        "sign_rule": "graded",
                    })
    return constants


def _inverse(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    size = len(matrix)
    augmented = [
        list(row) + [Fraction(int(i == j)) for j in range(size)]
        for i, row in enumerate(matrix)
    ]
    for column in range(size):
        pivot = next((row for row in range(column, size) if augmented[row][column]), None)
        if pivot is None:
            raise ValueError("Generator realization matrix is singular")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        divisor = augmented[column][column]
        augmented[column] = [value / divisor for value in augmented[column]]
        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            if factor:
                augmented[row] = [
                    value - factor * pivot_value
                    for value, pivot_value in zip(augmented[row], augmented[column])
                ]
    return [row[size:] for row in augmented]


def build_schema(n: int) -> dict[str, object]:
    even, odd = build_basis(n)
    realizations, forms = build_realizations(n)
    algebra_name = f"C({n + 1})"
    even_dimension = 2 * n * n + n + 1
    odd_dimension = 4 * n
    all_labels = even + odd
    parity = {label: int(label in odd) for label in all_labels}
    oscillator_labels = list(oscillator_order(n))
    realization_entries = {
        label: {
            "standard_form": _standard_form(realizations[label]),
            "frappat_form": forms[label],
            "parity": parity[label],
        }
        for label in all_labels
    }
    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": algebra_name,
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
                "count": 2,
                "labels": ["a_1_p", "a_1_m"],
                "parity": 1,
                "description": "Standard fermionic pair a_1^+, a_1^-",
            },
            "bosons": {
                "n": n,
                "count": 2 * n,
                "labels": [label for label in oscillator_labels if label.startswith("b_")],
                "parity": 0,
                "description": f"Bosonic oscillators b_i^+, b_i^- for i=1,...,{n}",
            },
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relation for one standard fermion pair",
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
                "description": "Bosons commute with fermions in the undeformed oscillator algebra",
                "boson_fermion": "[b_i^±, a_1^±] = 0",
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
                "identity": True,
                "relation": "K = 1",
                "included_in_basis": False,
            },
        },
        "basis": {
            "even": even,
            "odd": odd,
            "ordering_convention": "PBW: [odd generators] < [even generators]; K=1 and κ are excluded from the C(n+1) basis",
        },
        "parity": parity,
        "generator_realization": {
            "description": "Standard form with PBW ordering",
            "ordering": ", ".join(oscillator_labels),
            "realizations": realization_entries,
        },
        "structure_constants": _structure_constants(even, odd, realizations, n),
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


def generate(n: int, output_dir: Path = DATA_DIR) -> Path:
    schema = build_schema(n)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"C_{n}_structure.json"
    path.write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, nargs="+", default=[1, 2, 3], help="bosonic rank(s)")
    parser.add_argument("--output-dir", type=Path, default=DATA_DIR)
    args = parser.parse_args()
    for rank in args.n:
        print(generate(rank, args.output_dir))


if __name__ == "__main__":
    main()
