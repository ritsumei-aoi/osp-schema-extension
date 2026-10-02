#!/usr/bin/env python3
"""Generate Schema 1 structure constants for C(n+1) = osp(2|2n)."""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Iterable


Word = tuple[str, ...]
Polynomial = dict[Word, Fraction]


def _variable_key(variable: str) -> tuple[int, int]:
    match = re.fullmatch(r"(?:a_1|b_(\d+))_([pm])", variable)
    if variable.startswith("a_1_"):
        return (0, 0 if variable.endswith("_p") else 1)
    if match is None:
        raise ValueError(f"Unknown oscillator variable: {variable}")
    return (int(match.group(1)), 0 if match.group(2) == "p" else 1)


@lru_cache(maxsize=None)
def _normal_order_word(word: Word) -> tuple[tuple[Word, Fraction], ...]:
    for index in range(len(word) - 1):
        left, right = word[index:index + 2]
        left_key, right_key = _variable_key(left), _variable_key(right)
        if left_key <= right_key:
            continue

        swapped = word[:index] + (right, left) + word[index + 2:]
        same_mode = left.split("_")[0:2] == right.split("_")[0:2]
        fermion_pair = same_mode and left.startswith("a_")
        swap_coefficient = Fraction(-1 if fermion_pair else 1)
        terms: dict[Word, Fraction] = {}
        for ordered, coefficient in _normal_order_word(swapped):
            terms[ordered] = terms.get(ordered, Fraction()) + (
                swap_coefficient * coefficient
            )

        if same_mode and left.endswith("_m") and right.endswith("_p"):
            contracted = word[:index] + word[index + 2:]
            contraction_coefficient = Fraction(1)
            for ordered, coefficient in _normal_order_word(contracted):
                terms[ordered] = terms.get(ordered, Fraction()) + (
                    contraction_coefficient * coefficient
                )
        return tuple((monomial, coefficient) for monomial, coefficient in terms.items()
                     if coefficient)

    fermions = [variable for variable in word if variable.startswith("a_")]
    if len(fermions) != len(set(fermions)):
        return ()
    return ((word, Fraction(1)),)


def _clean(poly: Polynomial) -> Polynomial:
    return {word: coefficient for word, coefficient in poly.items() if coefficient}


def _add(left: Polynomial, right: Polynomial) -> Polynomial:
    result = dict(left)
    for word, coefficient in right.items():
        result[word] = result.get(word, Fraction()) + coefficient
    return _clean(result)


def _scale(poly: Polynomial, coefficient: Fraction) -> Polynomial:
    return _clean({word: coefficient * value for word, value in poly.items()})


def _multiply(left: Polynomial, right: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for left_word, left_coefficient in left.items():
        for right_word, right_coefficient in right.items():
            for word, coefficient in _normal_order_word(left_word + right_word):
                result[word] = result.get(word, Fraction()) + (
                    left_coefficient * right_coefficient * coefficient
                )
    return _clean(result)


def _word_poly(word: Iterable[str], coefficient: Fraction = Fraction(1)) -> Polynomial:
    result: Polynomial = {}
    for ordered, value in _normal_order_word(tuple(word)):
        result[ordered] = coefficient * value
    return _clean(result)


def _superbracket(
    left: Polynomial, right: Polynomial, left_parity: int, right_parity: int
) -> Polynomial:
    sign = -1 if left_parity and right_parity else 1
    return _add(_multiply(left, right), _scale(_multiply(right, left), Fraction(-sign)))


def _negative_root_label(label: str) -> str:
    replacements = {
        "_p": "_m",
        "_m": "_p",
        "_pp": "_mm",
        "_pm": "_mp",
        "_mp": "_pm",
        "_mm": "_pp",
    }
    for suffix in ("_pp", "_pm", "_mp", "_mm", "_p", "_m"):
        if label.endswith(suffix):
            return label[:-len(suffix)] + replacements[suffix]
    raise ValueError(f"Cannot negate root label: {label}")


def _root_generators(n: int) -> tuple[list[tuple[str, Polynomial]],
                                      list[tuple[str, Polynomial]]]:
    even_positive: list[tuple[str, Polynomial]] = []
    odd_positive: list[tuple[str, Polynomial]] = []

    for i in range(1, n + 1):
        even_positive.append((
            f"E_2del{i}_p", _word_poly((f"b_{i}_p", f"b_{i}_p"))
        ))
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even_positive.append((
                f"E_del{i}_del{j}_pp",
                _word_poly((f"b_{i}_p", f"b_{j}_p")),
            ))
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even_positive.append((
                f"E_del{i}_del{j}_pm",
                _word_poly((f"b_{i}_p", f"b_{j}_m")),
            ))

    for i in range(1, n + 1):
        odd_positive.append((
            f"E_eps_del{i}_pm", _word_poly(("a_1_p", f"b_{i}_m"))
        ))
    for i in range(1, n + 1):
        odd_positive.append((
            f"E_eps_del{i}_pp", _word_poly(("a_1_p", f"b_{i}_p"))
        ))

    even_negative = [
        (_negative_root_label(label), _opposite_polynomial(poly))
        for label, poly in reversed(even_positive)
    ]
    odd_negative = [
        (_negative_root_label(label), _opposite_polynomial(poly))
        for label, poly in reversed(odd_positive)
    ]
    return even_negative + even_positive, odd_negative + odd_positive


def _opposite_polynomial(poly: Polynomial) -> Polynomial:
    flipped = {
        word: coefficient for word, coefficient in poly.items()
    }
    return _clean({
        tuple(
            variable[:-1] + ("m" if variable.endswith("_p") else "p")
            for variable in word
        ): coefficient
        for word, coefficient in flipped.items()
    })


def _cartan_generators(n: int) -> list[tuple[str, Polynomial]]:
    cartan: list[tuple[str, Polynomial]] = []
    h1 = _add(
        _word_poly(("a_1_p", "a_1_m")),
        _word_poly(("b_1_p", "b_1_m")),
    )
    cartan.append(("H_1", h1))

    for k in range(2, n + 1):
        cartan.append((
            f"H_{k}",
            _add(
                _word_poly((f"b_{k - 1}_p", f"b_{k - 1}_m")),
                _scale(_word_poly((f"b_{k}_p", f"b_{k}_m")), Fraction(-1)),
            ),
        ))
    terminal = _add(
        _scale(_word_poly((f"b_{n}_p", f"b_{n}_m")), Fraction(-1)),
        {(): Fraction(-1, 2)},
    )
    cartan.append((f"H_{n + 1}", terminal))
    return cartan


def _format_fraction(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else str(value)


def _format_word(word: Word) -> str:
    names = {
        "a_1_p": "a_1^+",
        "a_1_m": "a_1^-",
    }
    for variable in word:
        if variable not in names:
            match = re.fullmatch(r"b_(\d+)_([pm])", variable)
            if match is None:
                raise ValueError(f"Unknown oscillator variable: {variable}")
            names[variable] = f"b_{match.group(1)}^{'+' if match.group(2) == 'p' else '-'}"
    return " ".join(names[variable] for variable in word) or "1"


def _ordered_terms(poly: Polynomial) -> list[tuple[Word, Fraction]]:
    return sorted(poly.items(), key=lambda item: tuple(_variable_key(v) for v in item[0]))


def _frappat_form(poly: Polynomial) -> str:
    pieces: list[str] = []
    for word, coefficient in _ordered_terms(poly):
        magnitude = abs(coefficient)
        term = _format_word(word)
        if magnitude != 1 or not word:
            term = f"{_format_fraction(magnitude)}" + (f" {term}" if word else "")
        if not pieces:
            pieces.append(("-" if coefficient < 0 else "") + term)
        else:
            pieces.append((" - " if coefficient < 0 else " + ") + term)
    return "".join(pieces) if pieces else "0"


def _basis_expansion(
    basis: list[tuple[str, Polynomial]], target: Polynomial, context: str
) -> dict[str, Fraction]:
    monomials = sorted(
        set(target).union(*(set(poly) for _, poly in basis)),
        key=lambda word: tuple(_variable_key(v) for v in word),
    )
    rows = [
        [poly.get(word, Fraction()) for _, poly in basis]
        + [target.get(word, Fraction())]
        for word in monomials
    ]
    pivot_row = 0
    for column in range(len(basis)):
        pivot = next(
            (row for row in range(pivot_row, len(rows)) if rows[row][column]),
            None,
        )
        if pivot is None:
            raise ValueError("Generator basis is linearly dependent")
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        scale = rows[pivot_row][column]
        rows[pivot_row] = [value / scale for value in rows[pivot_row]]
        for row in range(len(rows)):
            if row == pivot_row or not rows[row][column]:
                continue
            factor = rows[row][column]
            rows[row] = [
                value - factor * pivot_value
                for value, pivot_value in zip(rows[row], rows[pivot_row])
            ]
        pivot_row += 1

    if any(row[-1] for row in rows[pivot_row:]):
        raise ValueError(f"Oscillator bracket does not close on the basis: {context}")
    return {
        label: rows[index][-1]
        for index, (label, _) in enumerate(basis)
        if rows[index][-1]
    }


def _realization_entry(poly: Polynomial, parity: int) -> dict:
    terms = [
        {"words": list(word), "coeff": _format_fraction(coefficient)}
        for word, coefficient in _ordered_terms(poly)
    ]
    return {
        "standard_form": terms,
        "frappat_form": _frappat_form(poly),
        "parity": parity,
    }


def build_schema(n: int, generation_date: str | None = None) -> dict:
    if n < 1:
        raise ValueError("Bosonic rank n must be at least 1")

    even_roots, odd_roots = _root_generators(n)
    cartan = _cartan_generators(n)
    ordered_basis = even_roots[0:len(even_roots) // 2]  # negative even roots
    ordered_basis += odd_roots[0:len(odd_roots) // 2]  # negative odd roots
    ordered_basis += cartan
    ordered_basis += even_roots[len(even_roots) // 2:]  # positive even roots
    ordered_basis += odd_roots[len(odd_roots) // 2:]  # positive odd roots

    # Root lists contain each parity's negative and positive halves; preserve
    # the selected PBW order while separating the schema's parity arrays.
    parities = {
        label: 0 for label, _ in even_roots
    }
    parities.update({label: 1 for label, _ in odd_roots})
    parities.update({label: 0 for label, _ in cartan})
    even_basis = [label for label, _ in ordered_basis if parities[label] == 0]
    odd_basis = [label for label, _ in ordered_basis if parities[label] == 1]
    realizations = {label: poly for label, poly in ordered_basis}

    basis_pairs = [
        (label, realizations[label], parities[label])
        for label, _ in ordered_basis
    ]
    structure_constants: list[dict[str, str]] = []
    for left_index, (left_label, left_poly, left_parity) in enumerate(basis_pairs):
        for right_label, right_poly, right_parity in basis_pairs[left_index:]:
            bracket = _superbracket(
                left_poly, right_poly, left_parity, right_parity
            )
            if not bracket:
                continue
            expansion = _basis_expansion(
                [(label, poly) for label, poly, _ in basis_pairs],
                bracket,
                f"[{left_label},{right_label}]",
            )
            for result_label, coefficient in expansion.items():
                structure_constants.append({
                    "X": left_label,
                    "Y": right_label,
                    "Z": result_label,
                    "coeff": _format_fraction(coefficient),
                    "sign_rule": "graded",
                })

    dimension_even = 2 * n * n + n + 1
    dimension_odd = 4 * n
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
                "total": dimension_even + dimension_odd,
                "even": dimension_even,
                "odd": dimension_odd,
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
                "description": "One standard fermionic creation/annihilation pair",
            },
            "bosons": {
                "rank": n,
                "count": 2 * n,
                "labels": [
                    label for i in range(1, n + 1)
                    for label in (f"b_{i}_p", f"b_{i}_m")
                ],
                "parity": 0,
                "description": f"Bosonic oscillators b_i^± for i=1,...,{n}",
            },
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations for a_1^±",
                "relations": {
                    "same_type": "{a_1^+, a_1^+} = {a_1^-, a_1^-} = 0",
                    "conjugate_pair": "{a_1^-, a_1^+} = 1",
                },
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations for b_i^±",
                "relations": {
                    "same_type": "[b_i^±, b_j^±] = 0 for all i,j",
                    "conjugate_pair": "[b_i^-, b_j^+] = δ_ij",
                },
            },
            "mixed_commutators": {
                "fermion_boson": "[a_1^±, b_i^±] = 0 for all i and signs",
            },
        },
        "central_elements": {
            "kappa": {
                "parity": 1,
                "nilpotent": True,
                "description": "Odd formal parameter for the central extension",
            },
            "K": {
                "parity": 0,
                "value": "1",
                "description": (
                    "Even central identity; excluded from the independent basis"
                ),
            },
        },
        "basis": {
            "even": even_basis,
            "odd": odd_basis,
            "ordering_convention": (
                "PBW: negative even < negative odd < Cartan < positive even "
                "< positive odd; K and kappa excluded"
            ),
        },
        "parity": parities,
        "generator_realization": {
            "description": "Normal-ordered oscillator realization",
            "ordering": [
                "a_1_p", "a_1_m",
                *[
                    label for i in range(1, n + 1)
                    for label in (f"b_{i}_p", f"b_{i}_m")
                ],
            ],
            "realizations": {
                label: _realization_entry(poly, parities[label])
                for label, poly in ordered_basis
            },
        },
        "structure_constants": structure_constants,
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": generation_date or date.today().isoformat(),
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "docs/math/Cn1_definition.md",
            ],
        },
    }


def validate_schema(schema: dict) -> None:
    n = schema["algebra"]["n"]
    even_basis, odd_basis = schema["basis"]["even"], schema["basis"]["odd"]
    all_labels = set(even_basis + odd_basis)
    if len(all_labels) != len(even_basis) + len(odd_basis):
        raise ValueError("Basis contains duplicate labels")
    if len(even_basis) != 2 * n * n + n + 1 or len(odd_basis) != 4 * n:
        raise ValueError("Basis counts do not match the dimension formulas")
    if set(schema["parity"]) != all_labels:
        raise ValueError("Parity map does not cover exactly the basis")
    if any(schema["parity"][label] != 0 for label in even_basis):
        raise ValueError("An even basis generator has odd parity")
    if any(schema["parity"][label] != 1 for label in odd_basis):
        raise ValueError("An odd basis generator has even parity")
    if set(schema["generator_realization"]["realizations"]) != all_labels:
        raise ValueError("Realizations do not cover exactly the basis")
    for bracket in schema["structure_constants"]:
        if not {bracket["X"], bracket["Y"], bracket["Z"]} <= all_labels:
            raise ValueError(f"Structure constant references an unknown label: {bracket}")
        Fraction(bracket["coeff"])
        if bracket["sign_rule"] != "graded":
            raise ValueError("Structure constant must use the graded sign rule")


def write_schemas(output_dir: Path, ranks: Iterable[int] = (1, 2, 3)) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for n in ranks:
        schema = build_schema(n)
        validate_schema(schema)
        output = output_dir / f"C_{n}_structure.json"
        output.write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")
        written.append(output)
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("data"))
    parser.add_argument("--ranks", type=int, nargs="+", default=[1, 2, 3])
    args = parser.parse_args()
    for path in write_schemas(args.output_dir, args.ranks):
        print(path)


if __name__ == "__main__":
    main()
