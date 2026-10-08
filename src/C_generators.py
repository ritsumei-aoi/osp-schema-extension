#!/usr/bin/env python3
"""Generate exact Schema 1 structure constants for C(n+1)."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import date
from fractions import Fraction
from pathlib import Path


def _atom_order(atom):
    if atom[0] == "a":
        return (0, 0 if atom[1] == "p" else 1)
    return (1, atom[1], 0 if atom[2] == "p" else 1)


def _normal_order_word(word):
    """Return a polynomial of canonical words using CAR and CCR relations."""
    for index in range(len(word) - 1):
        left, right = word[index:index + 2]
        if left[0] == right[0] == "a" and left == right:
            return {}
        if _atom_order(left) <= _atom_order(right):
            continue

        swapped = word[:index] + (right, left) + word[index + 2:]
        if left[0] == right[0] == "a":
            # a_1^- a_1^+ = 1 - a_1^+ a_1^-
            reordered = _normal_order_word(swapped)
            contracted = _normal_order_word(word[:index] + word[index + 2:])
            result = defaultdict(Fraction)
            for term, coeff in reordered.items():
                result[term] -= coeff
            for term, coeff in contracted.items():
                result[term] += coeff
            return {term: coeff for term, coeff in result.items() if coeff}
        if (
            left[0] == right[0] == "b"
            and left[1] == right[1]
        ):
            # b_i^- b_i^+ = b_i^+ b_i^- + 1
            reordered = _normal_order_word(swapped)
            contracted = _normal_order_word(word[:index] + word[index + 2:])
            result = defaultdict(Fraction)
            for term, coeff in reordered.items():
                result[term] += coeff
            for term, coeff in contracted.items():
                result[term] += coeff
            return {term: coeff for term, coeff in result.items() if coeff}
        return _normal_order_word(swapped)
    return {word: Fraction(1)}


def _add_scaled(target, source, scale=Fraction(1)):
    for word, coeff in source.items():
        target[word] += scale * coeff
        if not target[word]:
            del target[word]


def _multiply(left, right):
    result = defaultdict(Fraction)
    for left_word, left_coeff in left.items():
        for right_word, right_coeff in right.items():
            normalized = _normal_order_word(left_word + right_word)
            _add_scaled(result, normalized, left_coeff * right_coeff)
    return dict(result)


def _bracket(left, right, left_parity, right_parity):
    result = defaultdict(Fraction)
    _add_scaled(result, _multiply(left, right))
    _add_scaled(
        result,
        _multiply(right, left),
        -1 if left_parity * right_parity % 2 == 0 else 1,
    )
    return dict(result)


def _single_atom(name):
    if name.startswith("a_1_"):
        return ("a", name[-1])
    prefix, index, sign = name.split("_")
    if prefix != "b":
        raise ValueError(f"Unknown oscillator label: {name}")
    return ("b", int(index), sign)


def _word(*labels):
    return tuple(_single_atom(label) for label in labels)


def _generator_data(n):
    generators = {}
    parity = {}
    forms = {}

    def add(label, p, terms, form):
        polynomial = defaultdict(Fraction)
        for labels, coeff in terms:
            normalized = _normal_order_word(_word(*labels))
            _add_scaled(polynomial, normalized, Fraction(coeff))
        generators[label] = dict(polynomial)
        parity[label] = p
        forms[label] = form

    for k in range(1, n + 1):
        if k == 1:
            add(
                "H_1",
                0,
                [
                    (("a_1_p", "a_1_m"), 1),
                    (("b_1_p", "b_1_m"), 1),
                ],
                "a_1^+ a_1^- + b_1^+ b_1^-",
            )
        else:
            add(
                f"H_{k}",
                0,
                [
                    ((f"b_{k - 1}_p", f"b_{k - 1}_m"), 1),
                    ((f"b_{k}_p", f"b_{k}_m"), -1),
                ],
                f"b_{k - 1}^+ b_{k - 1}^- - b_{k}^+ b_{k}^-",
            )
    add(
        f"H_{n + 1}",
        0,
        [((f"b_{n}_p", f"b_{n}_m"), -1), ((), Fraction(-1, 2))],
        f"-b_{n}^+ b_{n}^- - 1/2",
    )

    for i in range(1, n + 1):
        for sign, suffix in (("p", "p"), ("m", "m")):
            label = f"E_2del{i}_{suffix}"
            atom = f"b_{i}_{sign}"
            add(label, 0, [((atom, atom), 1)], f"(b_{i}^{'+' if sign == 'p' else '-'})^2")

    sign_pairs = (("pp", "p", "p"), ("pm", "p", "m"),
                  ("mp", "m", "p"), ("mm", "m", "m"))
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            for suffix, sign_i, sign_j in sign_pairs:
                add(
                    f"E_del{i}_del{j}_{suffix}",
                    0,
                    [((f"b_{i}_{sign_i}", f"b_{j}_{sign_j}"), 1)],
                    f"b_{i}^{'+' if sign_i == 'p' else '-'} "
                    f"b_{j}^{'+' if sign_j == 'p' else '-'}",
                )

    for i in range(1, n + 1):
        for suffix, fermion_sign, boson_sign in sign_pairs:
            fermion = "a_1_p" if fermion_sign == "p" else "a_1_m"
            boson = f"b_{i}_{boson_sign}"
            add(
                f"E_eps1_del{i}_{suffix}",
                1,
                [((fermion, boson), 1)],
                f"a_1^{ '+' if fermion_sign == 'p' else '-' } "
                f"b_{i}^{ '+' if boson_sign == 'p' else '-' }",
            )
    return generators, parity, forms


def _pbw_order(n):
    labels = [f"H_{i}" for i in range(1, n + 2)]
    labels.extend(f"E_2del{i}_p" for i in range(1, n + 1))
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            labels.extend(
                (f"E_del{i}_del{j}_pp", f"E_del{i}_del{j}_pm")
            )
    for i in range(1, n + 1):
        labels.extend(
            (f"E_eps1_del{i}_pp", f"E_eps1_del{i}_pm")
        )
    for i in range(1, n + 1):
        labels.extend(
            (f"E_eps1_del{i}_mp", f"E_eps1_del{i}_mm")
        )
    labels.extend(f"E_2del{i}_m" for i in range(1, n + 1))
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            labels.extend(
                (f"E_del{i}_del{j}_mp", f"E_del{i}_del{j}_mm")
            )
    return labels


def _decompose(target, generators, labels):
    words = set(target)
    for label in labels:
        words.update(generators[label])
    ordered_words = sorted(words, key=lambda item: (_atom_order_key(item), item))
    matrix = [
        [generators[label].get(word, Fraction(0)) for label in labels]
        + [target.get(word, Fraction(0))]
        for word in ordered_words
    ]
    pivot_row = 0
    pivots = []
    for column in range(len(labels)):
        pivot = next(
            (row for row in range(pivot_row, len(matrix))
             if matrix[row][column]),
            None,
        )
        if pivot is None:
            continue
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
        pivots.append(column)
        pivot_row += 1

    for row in matrix:
        if not any(row[:-1]) and row[-1]:
            raise ValueError("Oscillator bracket is outside the declared basis")
    if len(pivots) != len(labels):
        raise ValueError("Declared oscillator basis is linearly dependent")
    coefficients = [Fraction(0)] * len(labels)
    for row, column in enumerate(pivots):
        coefficients[column] = matrix[row][-1]
    return {
        label: coeff
        for label, coeff in zip(labels, coefficients)
        if coeff
    }


def _atom_order_key(word):
    return tuple(_atom_order(atom) for atom in word)


def _fraction_string(value):
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _realization(label, polynomial, form, parity):
    standard_form = []
    for word, coeff in sorted(
        polynomial.items(), key=lambda item: (_atom_order_key(item[0]), item[0])
    ):
        standard_form.append({
            "words": [
                (
                    f"a_1_{atom[1]}"
                    if atom[0] == "a"
                    else f"b_{atom[1]}_{atom[2]}"
                )
                for atom in word
            ],
            "coeff": _fraction_string(coeff),
        })
    return {
        "standard_form": standard_form,
        "frappat_form": form,
        "parity": parity,
    }


def build_schema(n, generation_date=None):
    """Build a complete C(n+1) Schema 1 document for bosonic rank n."""
    if not isinstance(n, int) or n < 1:
        raise ValueError("n must be a positive integer")
    generators, parity, forms = _generator_data(n)
    pbw = _pbw_order(n)
    even = [label for label in generators if parity[label] == 0]
    odd = [label for label in generators if parity[label] == 1]

    constants = []
    for i, x in enumerate(pbw):
        for y in pbw[i:]:
            bracket = _bracket(
                generators[x], generators[y], parity[x], parity[y]
            )
            if not bracket:
                continue
            result = _decompose(bracket, generators, pbw)
            for z, coeff in result.items():
                constants.append({
                    "X": x,
                    "Y": y,
                    "Z": z,
                    "coeff": _fraction_string(coeff),
                    "sign_rule": "graded",
                })

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
                "labels": ["a_1_p", "a_1_m"],
                "parity": 1,
                "description": "Standard fermionic pair a_1^+, a_1^-",
            },
            "bosons": {
                "count": 2 * n,
                "n": n,
                "labels": [
                    label
                    for i in range(1, n + 1)
                    for label in (f"b_{i}_p", f"b_{i}_m")
                ],
                "parity": 0,
                "description": "Bosonic oscillators b_i^+, b_i^- for i=1,...,n",
            },
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations for a_1^+, a_1^-",
                "relations": {
                    "conjugate_pair": "{a_1_m, a_1_p} = 1",
                    "same_type": "{a_1_p, a_1_p} = {a_1_m, a_1_m} = 0",
                },
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations for bosonic oscillators",
                "relations": {
                    "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
                    "conjugate_pair": "[b_i_m, b_j_p] = δ_ij",
                },
            },
            "mixed_commutators": {
                "description": "Fermionic and bosonic oscillators commute",
                "relations": {"boson_fermion": "[b_i^±, a_1^±] = 0"},
            },
        },
        "central_elements": {
            "kappa": {
                "parity": 1,
                "central": True,
                "nilpotent": True,
                "relation": "kappa^2 = 0",
                "description": "Odd central symbol for the inhomogeneous extension",
            },
            "K": {
                "parity": 0,
                "central": True,
                "identity": True,
                "relation": "K = 1",
                "description": "Even central identity; identified with the scalar 1",
            },
        },
        "basis": {
            "even": even,
            "odd": odd,
            "ordering_convention": (
                "Cartan < positive even < positive odd < negative odd < "
                "negative even; indices and sign labels ordered as in "
                "handover/notation.md"
            ),
        },
        "parity": parity,
        "generator_realization": {
            "description": "Standard form with PBW-ordered oscillator words",
            "ordering": [
                "a_1_p", "a_1_m",
                *[
                    label
                    for i in range(1, n + 1)
                    for label in (f"b_{i}_p", f"b_{i}_m")
                ],
            ],
            "realizations": {
                label: _realization(
                    label, generators[label], forms[label], parity[label]
                )
                for label in pbw
            },
        },
        "structure_constants": constants,
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": generation_date or date.today().isoformat(),
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "docs/math/Cn1_definition.md",
                "handover/notation.md",
            ],
        },
    }


def generate_files(output_dir, ranks=(1, 2, 3), generation_date=None):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    paths = []
    for n in ranks:
        schema = build_schema(n, generation_date=generation_date)
        path = output_path / f"C_{n}_structure.json"
        path.write_text(
            json.dumps(schema, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        paths.append(path)
    return paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="data")
    parser.add_argument("--ranks", nargs="+", type=int, default=[1, 2, 3])
    args = parser.parse_args()
    for path in generate_files(args.output_dir, args.ranks):
        print(path)


if __name__ == "__main__":
    main()
