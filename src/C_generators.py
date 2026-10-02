#!/usr/bin/env python3
"""Generate Schema 1 structure constants for C(n+1), n=1,2,3."""

from __future__ import annotations

import json
from datetime import date
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from typing import TypeAlias

import sympy as sp

Word: TypeAlias = tuple[str, ...]
Polynomial: TypeAlias = dict[Word, Fraction]


def _oscillator_order(n: int) -> dict[str, int]:
    labels = ["a_1_p", "a_1_m"]
    for k in range(1, n + 1):
        labels.extend((f"b_{k}_p", f"b_{k}_m"))
    return {label: index for index, label in enumerate(labels)}


def _add(*polynomials: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for polynomial in polynomials:
        for word, coeff in polynomial.items():
            result[word] = result.get(word, Fraction()) + coeff
    return {word: coeff for word, coeff in result.items() if coeff}


def _scale(polynomial: Polynomial, coeff: Fraction) -> Polynomial:
    return {word: value * coeff for word, value in polynomial.items() if value * coeff}


def _normal_order_word(word: Word, order: dict[str, int]) -> Polynomial:
    for index in range(len(word) - 1):
        left, right = word[index:index + 2]
        left_rank, right_rank = order[left], order[right]
        is_fermion = left.startswith("a_1_")
        if left == right and is_fermion:
            return {}
        if left_rank <= right_rank:
            continue

        prefix, suffix = word[:index], word[index + 2:]
        swapped = prefix + (right, left) + suffix
        if left == "a_1_m" and right == "a_1_p":
            return _add(
                _normal_order_word(prefix + suffix, order),
                _scale(_normal_order_word(swapped, order), Fraction(-1)),
            )
        if left.startswith("b_") and right.startswith("b_"):
            same_mode = left.split("_")[1] == right.split("_")[1]
            if same_mode and left.endswith("_m") and right.endswith("_p"):
                return _add(
                    _normal_order_word(prefix + suffix, order),
                    _normal_order_word(swapped, order),
                )
        return _normal_order_word(swapped, order)
    return {word: Fraction(1)}


def _word(polynomial: Polynomial, factors: tuple[str, ...], order: dict[str, int],
          coeff: Fraction = Fraction(1)) -> Polynomial:
    if not coeff:
        return polynomial
    normalized = _normal_order_word(factors, order)
    return _add(polynomial, _scale(normalized, coeff))


def _multiply(left: Polynomial, right: Polynomial, order: dict[str, int]) -> Polynomial:
    result: Polynomial = {}
    for left_word, left_coeff in left.items():
        for right_word, right_coeff in right.items():
            term = _normal_order_word(left_word + right_word, order)
            result = _add(result, _scale(term, left_coeff * right_coeff))
    return result


def _linear_combination(*terms: tuple[tuple[str, ...], str],
                        order: dict[str, int]) -> Polynomial:
    result: Polynomial = {}
    for factors, coeff in terms:
        result = _word(result, factors, order, Fraction(coeff))
    return result


def _generators(n: int) -> tuple[list[str], list[str], dict[str, Polynomial]]:
    order = _oscillator_order(n)
    even: list[str] = [f"H_{k}" for k in range(1, n + 2)]
    odd = [
        *(f"E_eps1_del{k}_pp" for k in range(1, n + 1)),
        *(f"E_eps1_del{k}_pm" for k in range(1, n + 1)),
        *(f"E_eps1_del{k}_mp" for k in range(1, n + 1)),
        *(f"E_eps1_del{k}_mm" for k in range(1, n + 1)),
    ]
    even.extend(f"E_2del{k}_p" for k in range(1, n + 1))
    pairs = list(combinations(range(1, n + 1), 2))
    even.extend(f"E_del{i}_del{j}_pp" for i, j in pairs)
    even.extend(f"E_del{i}_del{j}_pm" for i, j in pairs)
    even.extend(f"E_2del{k}_m" for k in range(1, n + 1))
    even.extend(f"E_del{i}_del{j}_mm" for i, j in pairs)
    even.extend(f"E_del{i}_del{j}_mp" for i, j in pairs)

    realizations: dict[str, Polynomial] = {}
    realizations["H_1"] = _linear_combination(
        (("a_1_p", "a_1_m"), "1"), (("b_1_p", "b_1_m"), "1"), order=order
    )
    for k in range(2, n + 1):
        realizations[f"H_{k}"] = _linear_combination(
            ((f"b_{k - 1}_p", f"b_{k - 1}_m"), "1"),
            ((f"b_{k}_p", f"b_{k}_m"), "-1"),
            order=order,
        )
    realizations[f"H_{n + 1}"] = _linear_combination(
        ((f"b_{n}_p", f"b_{n}_m"), "-1"), ((), "-1/2"), order=order
    )
    for k in range(1, n + 1):
        realizations[f"E_2del{k}_p"] = _linear_combination(
            ((f"b_{k}_p", f"b_{k}_p"), "1/2"), order=order
        )
        realizations[f"E_2del{k}_m"] = _linear_combination(
            ((f"b_{k}_m", f"b_{k}_m"), "1/2"), order=order
        )
        for epsilon_sign, epsilon_label in (("p", "p"), ("m", "m")):
            for delta_sign, delta_label in (("p", "p"), ("m", "m")):
                name = f"E_eps1_del{k}_{epsilon_label}{delta_label}"
                realizations[name] = _linear_combination(
                    ((f"a_1_{epsilon_sign}", f"b_{k}_{delta_sign}"), "1"),
                    order=order,
                )
    for i, j in pairs:
        for suffix, factors in (
            ("pp", (f"b_{i}_p", f"b_{j}_p")),
            ("pm", (f"b_{i}_p", f"b_{j}_m")),
            ("mp", (f"b_{i}_m", f"b_{j}_p")),
            ("mm", (f"b_{i}_m", f"b_{j}_m")),
        ):
            realizations[f"E_del{i}_del{j}_{suffix}"] = _linear_combination(
                (factors, "1"), order=order
            )
    return even, odd, realizations


def _polynomial_bracket(left: Polynomial, right: Polynomial, left_parity: int,
                        right_parity: int, order: dict[str, int]) -> Polynomial:
    sign = -1 if left_parity * right_parity else 1
    return _add(
        _multiply(left, right, order),
        _scale(_multiply(right, left, order), Fraction(-sign)),
    )


def _coordinates(
    bracket: Polynomial,
    names: list[str],
    realizations: dict[str, Polynomial],
) -> dict[str, Fraction]:
    words = sorted(
        set(bracket).union(*(set(realizations[name]) for name in names))
    )
    matrix = sp.Matrix([
        [sp.Rational(realizations[name].get(word, 0).numerator,
                     realizations[name].get(word, 0).denominator) for name in names]
        for word in words
    ])
    target = sp.Matrix([
        sp.Rational(bracket.get(word, 0).numerator, bracket.get(word, 0).denominator)
        for word in words
    ])
    pivot_rows = matrix.T.rref()[1]
    square = matrix[list(pivot_rows), :]
    coeffs = square.inv() * target[list(pivot_rows), :]
    if matrix * coeffs != target:
        raise ValueError("Oscillator bracket is not in the declared generator span")
    return {
        name: Fraction(int(coeffs[index]), 1)
        if coeffs[index].q == 1
        else Fraction(int(coeffs[index].p), int(coeffs[index].q))
        for index, name in enumerate(names)
        if coeffs[index]
    }


def _standard_form(polynomial: Polynomial) -> list[dict[str, object]]:
    terms = []
    for word, coeff in sorted(polynomial.items()):
        terms.append({
            "words": list(word),
            "coeff": str(coeff.numerator) if coeff.denominator == 1
            else f"{coeff.numerator}/{coeff.denominator}",
        })
    return terms


def generate_schema(n: int) -> dict[str, object]:
    if n < 1:
        raise ValueError("Bosonic rank n must be at least 1")
    even, odd, realizations = _generators(n)
    basis = even + odd
    parities = {name: int(name in odd) for name in basis}
    order = _oscillator_order(n)
    structure_constants = []
    for i, x in enumerate(basis):
        for y in basis[i:]:
            bracket = _polynomial_bracket(
                realizations[x], realizations[y], parities[x], parities[y], order
            )
            if not bracket:
                continue
            components = _coordinates(bracket, basis, realizations)
            if not components:
                raise ValueError(f"Nonzero bracket [{x}, {y}] has no basis component")
            if any(parities[z] != (parities[x] + parities[y]) % 2 for z in components):
                raise ValueError(f"Parity mismatch in bracket [{x}, {y}]")
            structure_constants.extend({
                "X": x, "Y": y, "Z": z,
                "coeff": str(coeff.numerator) if coeff.denominator == 1
                else f"{coeff.numerator}/{coeff.denominator}",
                "sign_rule": "graded",
            } for z, coeff in components.items())

    boson_labels = [
        label for k in range(1, n + 1) for label in (f"b_{k}_p", f"b_{k}_m")
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
                "even": len(even),
                "odd": len(odd),
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
                "count": 2 * n,
                "n": n,
                "labels": boson_labels,
                "parity": 0,
                "description": "Bosonic oscillators b_k^± for k=1,...,n",
            },
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations",
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
                "parity": 1,
                "central": True,
                "nilpotent": True,
                "relation": "kappa^2 = 0",
                "description": "Formal odd central element for the nilpotent extension",
            },
            "K": {
                "parity": 0,
                "central": True,
                "relation": "K = 1",
                "description": "Even central identity; identified with the scalar 1",
            },
        },
        "basis": {
            "even": even,
            "odd": odd,
            "ordering_convention": (
                "PBW: kappa < [odd roots in listed order] < "
                "[even generators in listed order]; K=1 is excluded"
            ),
        },
        "parity": parities,
        "generator_realization": {
            "description": "Standard form with PBW ordering",
            "ordering": ["a_1_p", "a_1_m", *boson_labels],
            "realizations": {
                name: {
                    "standard_form": _standard_form(polynomial),
                    "frappat_form": _frappat_form(name, n),
                    "parity": parities[name],
                }
                for name, polynomial in realizations.items()
            },
        },
        "structure_constants": structure_constants,
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": date.today().isoformat(),
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "Bakalov and Sullivan (2017)",
            ],
        },
    }


def _frappat_form(name: str, n: int) -> str:
    if name == "H_1":
        return "a_1^+ a_1^- + b_1^+ b_1^-"
    if name.startswith("H_"):
        k = int(name[2:])
        if k == n + 1:
            return f"-b_{n}^+ b_{n}^- - 1/2"
        return f"b_{k - 1}^+ b_{k - 1}^- - b_{k}^+ b_{k}^-"
    if name.startswith("E_2del"):
        _, root, sign = name.split("_")
        k = root.removeprefix("2del")
        oscillator = "+" if sign == "p" else "-"
        return f"1/2 (b_{k}^{oscillator})^2"
    if name.startswith("E_eps1_del"):
        k, signs = name.removeprefix("E_eps1_del").split("_")
        epsilon = "+" if signs[0] == "p" else "-"
        delta = "+" if signs[1] == "p" else "-"
        return f"a_1^{epsilon} b_{k}^{delta}"
    if name.startswith("E_del"):
        _, left, right, signs = name.split("_")
        i, j = left.removeprefix("del"), right.removeprefix("del")
        first = "+" if signs[0] == "p" else "-"
        second = "+" if signs[1] == "p" else "-"
        return f"b_{i}^{first} b_{j}^{second}"
    return name


def write_schemas(output_dir: Path | str = "data", ranks: tuple[int, ...] = (1, 2, 3)) -> None:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for n in ranks:
        schema = generate_schema(n)
        path = output_dir / f"C_{n}_structure.json"
        path.write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    write_schemas()
