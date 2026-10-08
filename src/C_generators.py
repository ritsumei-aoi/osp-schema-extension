#!/usr/bin/env python3
"""Generate Schema 1 structure data for C(n+1) = osp(2|2n)."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import date
from fractions import Fraction
from itertools import combinations
from math import comb, factorial
from pathlib import Path
from typing import TypeAlias

Monomial: TypeAlias = tuple[int, ...]
Polynomial: TypeAlias = dict[Monomial, Fraction]


@dataclass(frozen=True)
class Generator:
    label: str
    parity: int
    realization: Polynomial
    frappat_form: str


def _fraction_string(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _add_term(poly: Polynomial, monomial: Monomial, coeff: Fraction) -> None:
    if coeff:
        poly[monomial] = poly.get(monomial, Fraction()) + coeff
        if not poly[monomial]:
            del poly[monomial]


def _term(n: int, coeff: int | Fraction, *powers: int) -> Polynomial:
    if len(powers) != 2 + 2 * n:
        raise ValueError("monomial must specify both fermion powers and each boson pair")
    value = Fraction(coeff)
    return {tuple(powers): value} if value else {}


def _add(left: Polynomial, right: Polynomial, scale: Fraction = Fraction(1)) -> Polynomial:
    result = dict(left)
    for monomial, coeff in right.items():
        _add_term(result, monomial, scale * coeff)
    return result


def _scale(poly: Polynomial, coeff: Fraction) -> Polynomial:
    return {monomial: coeff * value for monomial, value in poly.items() if coeff * value}


def _fermion_product(ap: int, am: int, bp: int, bm: int) -> dict[tuple[int, int], Fraction]:
    if am and bp:
        terms: dict[tuple[int, int], Fraction] = {}
        if ap <= 1 and bm <= 1:
            terms[(ap, bm)] = Fraction(1)
        if ap + 1 <= 1 and bm + 1 <= 1:
            terms[(ap + 1, bm + 1)] = Fraction(-1)
        return terms
    plus, minus = ap + bp, am + bm
    if plus > 1 or minus > 1:
        return {}
    return {(plus, minus): Fraction(1)}


def _boson_product(p: int, m: int, q: int, r: int) -> dict[tuple[int, int], Fraction]:
    result: dict[tuple[int, int], Fraction] = {}
    for contractions in range(min(m, q) + 1):
        coeff = Fraction(comb(m, contractions) * factorial(q) // factorial(q - contractions))
        result[(p + q - contractions, m + r - contractions)] = coeff
    return result


def _multiply_monomials(left: Monomial, right: Monomial, n: int) -> Polynomial:
    fermion_terms = _fermion_product(left[0], left[1], right[0], right[1])
    if not fermion_terms:
        return {}
    boson_terms: dict[tuple[int, ...], Fraction] = {(): Fraction(1)}
    for k in range(n):
        offset = 2 + 2 * k
        single = _boson_product(
            left[offset], left[offset + 1], right[offset], right[offset + 1]
        )
        updated: dict[tuple[int, ...], Fraction] = {}
        for prefix, prefix_coeff in boson_terms.items():
            for pair, pair_coeff in single.items():
                powers = prefix + pair
                updated[powers] = updated.get(powers, Fraction()) + prefix_coeff * pair_coeff
        boson_terms = updated
    result: Polynomial = {}
    for (ap, am), fermion_coeff in fermion_terms.items():
        for boson_powers, boson_coeff in boson_terms.items():
            result[(ap, am) + boson_powers] = fermion_coeff * boson_coeff
    return result


def multiply(left: Polynomial, right: Polynomial, n: int) -> Polynomial:
    result: Polynomial = {}
    for left_monomial, left_coeff in left.items():
        for right_monomial, right_coeff in right.items():
            product = _multiply_monomials(left_monomial, right_monomial, n)
            for monomial, coeff in product.items():
                _add_term(result, monomial, left_coeff * right_coeff * coeff)
    return result


def graded_bracket(left: Polynomial, right: Polynomial, parity_left: int,
                   parity_right: int, n: int) -> Polynomial:
    sign = -1 if parity_left and parity_right else 1
    return _add(multiply(left, right, n), multiply(right, left, n), Fraction(-sign))


def _monomial(n: int, factors: tuple[tuple[int, str], ...]) -> Monomial:
    powers = [0] * (2 + 2 * n)
    for index, kind in factors:
        if kind == "a_p":
            offset = 0
        elif kind == "a_m":
            offset = 1
        else:
            offset = 2 + 2 * (index - 1) + (kind == "b_m")
        powers[offset] += 1
    return tuple(powers)


def _single(n: int, coeff: int | Fraction,
            factors: tuple[tuple[int, str], ...]) -> Polynomial:
    return _term(n, coeff, *_monomial(n, factors))


def build_generators(n: int) -> list[Generator]:
    if n < 1:
        raise ValueError("bosonic rank n must be positive")
    generators: list[Generator] = []
    cartan_terms: list[tuple[tuple[tuple[int, str], ...], Fraction]] = []
    cartan_terms.append((((1, "a_p"), (1, "a_m")), Fraction(1)))
    cartan_terms.append((((1, "b_p"), (1, "b_m")), Fraction(1)))
    generators.append(Generator(
        "H_1", 0,
        _add(_single(n, 1, cartan_terms[0][0]), _single(n, 1, cartan_terms[1][0])),
        "a_1^+ a_1^- + b_1^+ b_1^-",
    ))
    for k in range(2, n + 1):
        plus = ((k - 1, "b_p"), (k - 1, "b_m"))
        minus = ((k, "b_p"), (k, "b_m"))
        generators.append(Generator(
            f"H_{k}", 0,
            _add(_single(n, 1, plus), _single(n, -1, minus)),
            f"b_{k-1}^+ b_{k-1}^- - b_{k}^+ b_{k}^-",
        ))
    terminal = ((n, "b_p"), (n, "b_m"))
    generators.append(Generator(
        f"H_{n+1}", 0,
        _add(_single(n, -1, terminal), _term(n, Fraction(-1, 2), *_monomial(n, ()))),
        f"-b_{n}^+ b_{n}^- - 1/2",
    ))

    for sign, suffix, factor_kind in (
        ("p", "p", "b_p"),
        ("m", "m", "b_m"),
    ):
        for k in range(1, n + 1):
            coeff = Fraction(1, 2) if k == n else Fraction(1)
            word = ((k, factor_kind), (k, factor_kind))
            generators.append(Generator(
                f"E_2del{k}_{suffix}", 0, _single(n, coeff, word),
                (f"1/2*(b_{k}^{'+' if sign == 'p' else '-'})^2"
                 if coeff == Fraction(1, 2)
                 else f"(b_{k}^{'+' if sign == 'p' else '-'})^2"),
            ))

    for i, j in combinations(range(1, n + 1), 2):
        for suffix, left_kind, right_kind in (
            ("pp", "b_p", "b_p"),
            ("mm", "b_m", "b_m"),
            ("pm", "b_p", "b_m"),
            ("mp", "b_m", "b_p"),
        ):
            generators.append(Generator(
                f"E_del{i}_del{j}_{suffix}", 0,
                _single(n, 1, ((i, left_kind), (j, right_kind))),
                f"b_{i}^{'+' if left_kind == 'b_p' else '-'} "
                f"b_{j}^{'+' if right_kind == 'b_p' else '-'}",
            ))

    for k in range(1, n + 1):
        for suffix, fermion, boson in (
            ("pp", "a_p", "b_p"),
            ("pm", "a_p", "b_m"),
            ("mp", "a_m", "b_p"),
            ("mm", "a_m", "b_m"),
        ):
            generators.append(Generator(
                f"E_eps1_del{k}_{suffix}", 1,
                _single(n, 1, ((1, fermion), (k, boson))),
                f"a_1^{'+' if fermion == 'a_p' else '-'} "
                f"b_{k}^{'+' if boson == 'b_p' else '-'}",
            ))
    return generators


def _solve_in_basis(target: Polynomial, generators: list[Generator]) -> dict[str, Fraction]:
    rows = sorted({monomial for generator in generators
                   for monomial in generator.realization})
    if set(target) - set(rows):
        raise ValueError(f"bracket has monomials outside the basis span: {set(target) - set(rows)}")
    matrix = [
        [generator.realization.get(monomial, Fraction()) for generator in generators]
        + [target.get(monomial, Fraction())]
        for monomial in rows
    ]
    pivot_row = 0
    pivot_rows: list[int] = []
    for column in range(len(generators)):
        pivot = next((row for row in range(pivot_row, len(matrix))
                      if matrix[row][column]), None)
        if pivot is None:
            raise ValueError("generator realizations are linearly dependent")
        matrix[pivot_row], matrix[pivot] = matrix[pivot], matrix[pivot_row]
        divisor = matrix[pivot_row][column]
        matrix[pivot_row] = [entry / divisor for entry in matrix[pivot_row]]
        for row in range(len(matrix)):
            if row != pivot_row and matrix[row][column]:
                factor = matrix[row][column]
                matrix[row] = [
                    entry - factor * pivot_entry
                    for entry, pivot_entry in zip(matrix[row], matrix[pivot_row])
                ]
        pivot_rows.append(pivot_row)
        pivot_row += 1
    if any(not any(row[:-1]) and row[-1] for row in matrix):
        raise ValueError("bracket is not in the span of the generator basis")
    return {
        generators[column].label: matrix[row][-1]
        for column, row in enumerate(pivot_rows)
        if matrix[row][-1]
    }


def _word_from_monomial(monomial: Monomial) -> list[str]:
    words: list[str] = []
    if monomial[0]:
        words.extend(["a_1_p"] * monomial[0])
    if monomial[1]:
        words.extend(["a_1_m"] * monomial[1])
    for k in range((len(monomial) - 2) // 2):
        plus, minus = monomial[2 + 2 * k:4 + 2 * k]
        words.extend([f"b_{k+1}_p"] * plus)
        words.extend([f"b_{k+1}_m"] * minus)
    return words


def build_schema(n: int, generation_date: str | None = None) -> dict:
    generators = build_generators(n)
    even_basis = [generator.label for generator in generators if not generator.parity]
    odd_basis = [generator.label for generator in generators if generator.parity]
    parity = {generator.label: generator.parity for generator in generators}
    structure_constants = []
    for left_index, left in enumerate(generators):
        for right in generators[left_index:]:
            result = graded_bracket(
                left.realization, right.realization, left.parity, right.parity, n
            )
            if result:
                expansion = _solve_in_basis(result, generators)
                for label, coeff in expansion.items():
                    structure_constants.append({
                        "X": left.label,
                        "Y": right.label,
                        "Z": label,
                        "coeff": _fraction_string(coeff),
                        "sign_rule": "graded",
                    })

    realizations = {}
    for generator in generators:
        terms = [
            {"words": _word_from_monomial(monomial), "coeff": _fraction_string(coeff)}
            for monomial, coeff in sorted(generator.realization.items())
        ]
        record = {
            "standard_form": terms,
            "frappat_form": generator.frappat_form,
            "parity": generator.parity,
        }
        if generator.label == f"H_{n+1}":
            record["note"] = "Terminal Cartan; includes the -1/2 constant"
        realizations[generator.label] = record

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
                "osp": f"osp(2|{2*n})",
                "dimension_formula": "osp(2m|2n)",
            },
            "dimension": {
                "total": dimension_even + dimension_odd,
                "even": dimension_even,
                "odd": dimension_odd,
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
                    label for k in range(1, n + 1)
                    for label in (f"b_{k}_p", f"b_{k}_m")
                ],
                "parity": 0,
                "description": "Bosonic oscillators b_k^± for k=1,...,n",
            },
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations for the standard fermion pair",
                "relations": {
                    "{a_1_m, a_1_p}": "1",
                    "{a_1_p, a_1_p}": "0",
                    "{a_1_m, a_1_m}": "0",
                },
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations for bosonic oscillators",
                "relations": {
                    "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
                    "conjugate_pair": "[b_i^-, b_j^+] = δ_ij",
                },
            },
            "mixed_commutators": {
                "boson_fermion": "[b_i^±, a_1^±] = 0 in the undeformed oscillator algebra",
            },
        },
        "central_elements": {
            "kappa": {
                "label": "kappa",
                "parity": 1,
                "central": True,
                "nilpotent": True,
                "relation": "kappa^2 = 0",
                "description": "Formal odd central symbol for the inhomogeneous extension",
            },
            "K": {
                "label": "K",
                "parity": 0,
                "central": True,
                "identified_with_scalar_identity": True,
                "relation": "K = 1",
                "description": "Even central identity; excluded as an independent basis element",
            },
        },
        "basis": {
            "even": even_basis,
            "odd": odd_basis,
            "ordering_convention": "PBW: kappa < [odd] < [even]; K = 1 is excluded",
        },
        "parity": parity,
        "generator_realization": {
            "description": "Standard form with PBW-ordered oscillator words",
            "ordering": "a_1_p, a_1_m, b_1_p, b_1_m, ..., b_n_p, b_n_m",
            "realizations": realizations,
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


def generate_files(output_dir: Path, ranks: tuple[int, ...] = (1, 2, 3)) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_paths = []
    for n in ranks:
        path = output_dir / f"C_{n}_structure.json"
        path.write_text(json.dumps(build_schema(n), indent=2) + "\n", encoding="utf-8")
        output_paths.append(path)
    return output_paths


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data",
    )
    parser.add_argument("--ranks", type=int, nargs="+", default=(1, 2, 3))
    args = parser.parse_args()
    for path in generate_files(args.output_dir, tuple(args.ranks)):
        print(path)


if __name__ == "__main__":
    main()
