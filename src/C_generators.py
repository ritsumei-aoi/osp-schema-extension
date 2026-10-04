#!/usr/bin/env python3
"""Generate exact Schema 1 structure data for C(n+1) oscillator realizations."""

from __future__ import annotations

import argparse
import json
from datetime import date
from fractions import Fraction
from functools import lru_cache
from itertools import combinations
from pathlib import Path
from typing import Iterable

Monomial = tuple[str, ...]
Polynomial = dict[Monomial, Fraction]


def _add_scaled(
    target: Polynomial, source: Polynomial, scale: Fraction = Fraction(1)
) -> None:
    for word, coefficient in source.items():
        value = target.get(word, Fraction(0)) + scale * coefficient
        if value:
            target[word] = value
        else:
            target.pop(word, None)


def _normal_order(word: Monomial, token_order: dict[str, int]) -> Polynomial:
    for index in range(len(word) - 1):
        left, right = word[index : index + 2]
        if left == right and left.startswith("a_"):
            return {}
        if token_order[left] <= token_order[right]:
            continue
        prefix, suffix = word[:index], word[index + 2 :]

        if left == "a_1_m" and right == "a_1_p":
            result = _normal_order(prefix + suffix, token_order)
            _add_scaled(
                result,
                _normal_order(prefix + (right, left) + suffix, token_order),
                Fraction(-1),
            )
            return result

        if left.startswith("b_") and right.startswith("b_"):
            left_mode, left_sign = left.split("_")[1:]
            right_mode, right_sign = right.split("_")[1:]
            if left_mode == right_mode and left_sign == "m" and right_sign == "p":
                result = _normal_order(prefix + (right, left) + suffix, token_order)
                _add_scaled(result, _normal_order(prefix + suffix, token_order))
                return result

        return _normal_order(prefix + (right, left) + suffix, token_order)

    return {word: Fraction(1)}


def _multiply(
    left: Polynomial, right: Polynomial, token_order: dict[str, int]
) -> Polynomial:
    result: Polynomial = {}
    for left_word, left_coefficient in left.items():
        for right_word, right_coefficient in right.items():
            normalized = _normal_order(left_word + right_word, token_order)
            _add_scaled(result, normalized, left_coefficient * right_coefficient)
    return result


def _bracket(
    left: Polynomial,
    right: Polynomial,
    left_parity: int,
    right_parity: int,
    token_order: dict[str, int],
) -> Polynomial:
    result = _multiply(left, right, token_order)
    _add_scaled(
        result,
        _multiply(right, left, token_order),
        Fraction(-1 if left_parity * right_parity == 0 else 1),
    )
    return result


def _fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _make_generators(n: int) -> tuple[list[str], list[str], dict[str, Polynomial]]:
    token_order = {"a_1_p": 0, "a_1_m": 1}
    for k in range(1, n + 1):
        token_order[f"b_{k}_p"] = 2 * k
        token_order[f"b_{k}_m"] = 2 * k + 1

    def word(*tokens: str) -> Polynomial:
        return _normal_order(tuple(tokens), token_order)

    def sum_terms(*terms: tuple[Fraction, Polynomial]) -> Polynomial:
        result: Polynomial = {}
        for coefficient, polynomial in terms:
            _add_scaled(result, polynomial, coefficient)
        return result

    even: list[str] = [f"H_{k}" for k in range(1, n + 2)]
    even.extend(f"E_2del{k}_p" for k in range(1, n + 1))
    pairs = list(combinations(range(1, n + 1), 2))
    for i, j in pairs:
        even.extend((f"E_del{i}_del{j}_pp", f"E_del{i}_del{j}_pm"))
    even.extend(f"E_2del{k}_m" for k in range(1, n + 1))
    for i, j in pairs:
        even.extend((f"E_del{i}_del{j}_mm", f"E_del{i}_del{j}_mp"))
    odd = [
        f"E_eps1_del{k}_{signs}"
        for k in range(1, n + 1)
        for signs in ("pp", "pm", "mp", "mm")
    ]

    realizations: dict[str, Polynomial] = {
        "H_1": sum_terms(
            (Fraction(1), word("a_1_p", "a_1_m")),
            (Fraction(1), word("b_1_p", "b_1_m")),
        )
    }
    for k in range(2, n + 1):
        realizations[f"H_{k}"] = sum_terms(
            (Fraction(1), word(f"b_{k-1}_p", f"b_{k-1}_m")),
            (Fraction(-1), word(f"b_{k}_p", f"b_{k}_m")),
        )
    realizations[f"H_{n + 1}"] = sum_terms(
        (Fraction(-1), word(f"b_{n}_p", f"b_{n}_m")),
        (Fraction(-1, 2), {(): Fraction(1)}),
    )
    for k in range(1, n + 1):
        realizations[f"E_2del{k}_p"] = word(f"b_{k}_p", f"b_{k}_p")
        realizations[f"E_2del{k}_m"] = word(f"b_{k}_m", f"b_{k}_m")
    for i, j in pairs:
        realizations[f"E_del{i}_del{j}_pp"] = word(f"b_{i}_p", f"b_{j}_p")
        realizations[f"E_del{i}_del{j}_pm"] = word(f"b_{i}_p", f"b_{j}_m")
        realizations[f"E_del{i}_del{j}_mp"] = word(f"b_{i}_m", f"b_{j}_p")
        realizations[f"E_del{i}_del{j}_mm"] = word(f"b_{i}_m", f"b_{j}_m")
    for k in range(1, n + 1):
        realizations[f"E_eps1_del{k}_pp"] = word("a_1_p", f"b_{k}_p")
        realizations[f"E_eps1_del{k}_pm"] = word("a_1_p", f"b_{k}_m")
        realizations[f"E_eps1_del{k}_mp"] = word("a_1_m", f"b_{k}_p")
        realizations[f"E_eps1_del{k}_mm"] = word("a_1_m", f"b_{k}_m")

    return even, odd, realizations


def _coordinate_reducer(
    labels: Iterable[str], realizations: dict[str, Polynomial]
) -> tuple[list[tuple[Monomial, Polynomial, dict[str, Fraction]]], dict[str, int]]:
    pivots: list[tuple[Monomial, Polynomial, dict[str, Fraction]]] = []
    parities: dict[str, int] = {}
    for label in labels:
        vector = dict(realizations[label])
        coordinates = {label: Fraction(1)}
        for pivot, pivot_vector, pivot_coordinates in pivots:
            factor = vector.get(pivot, Fraction(0))
            if factor:
                _add_scaled(vector, pivot_vector, -factor)
                for basis_label, coefficient in pivot_coordinates.items():
                    value = coordinates.get(basis_label, Fraction(0)) - factor * coefficient
                    if value:
                        coordinates[basis_label] = value
                    else:
                        coordinates.pop(basis_label, None)
        if not vector:
            raise ValueError(f"Generator realization is linearly dependent: {label}")
        pivot = min(vector)
        factor = vector[pivot]
        normalized_vector = {key: value / factor for key, value in vector.items()}
        normalized_coordinates = {
            key: value / factor for key, value in coordinates.items()
        }
        pivots.append((pivot, normalized_vector, normalized_coordinates))
        parities[label] = int(label.startswith("E_eps1_"))
    return pivots, parities


def _decompose(
    polynomial: Polynomial,
    pivots: list[tuple[Monomial, Polynomial, dict[str, Fraction]]],
) -> dict[str, Fraction]:
    remainder = dict(polynomial)
    result: dict[str, Fraction] = {}
    for pivot, pivot_vector, pivot_coordinates in pivots:
        factor = remainder.get(pivot, Fraction(0))
        if factor:
            _add_scaled(remainder, pivot_vector, -factor)
            for label, coefficient in pivot_coordinates.items():
                value = result.get(label, Fraction(0)) + factor * coefficient
                if value:
                    result[label] = value
                else:
                    result.pop(label, None)
    if remainder:
        raise ValueError(f"Bracket is outside the generator span: {remainder}")
    return result


def _word_text(word: Monomial) -> str:
    return " ".join(token.replace("_p", "^+").replace("_m", "^-") for token in word)


def _realization_entry(
    polynomial: Polynomial, parity: int
) -> dict[str, object]:
    terms = []
    frappat_terms = []
    for word in sorted(polynomial, key=lambda item: (len(item), item)):
        coefficient = polynomial[word]
        terms.append({"words": list(word), "coeff": _fraction_text(coefficient)})
        oscillator_word = _word_text(word) or "1"
        if coefficient == 1:
            frappat_terms.append(oscillator_word)
        elif coefficient == -1:
            frappat_terms.append(f"-{oscillator_word}")
        else:
            frappat_terms.append(f"{_fraction_text(coefficient)} {oscillator_word}")
    return {
        "standard_form": terms,
        "frappat_form": " + ".join(frappat_terms).replace("+ -", "- "),
        "parity": parity,
    }


@lru_cache(maxsize=None)
def build_schema(n: int) -> dict[str, object]:
    if n < 1:
        raise ValueError("Bosonic rank n must be a positive integer")

    even, odd, realizations = _make_generators(n)
    pbw_labels = odd + even
    pivots, parity = _coordinate_reducer(pbw_labels, realizations)
    structure_constants: list[dict[str, str]] = []
    token_order = {"a_1_p": 0, "a_1_m": 1}
    for k in range(1, n + 1):
        token_order[f"b_{k}_p"] = 2 * k
        token_order[f"b_{k}_m"] = 2 * k + 1
    for left_index, left_label in enumerate(pbw_labels):
        for right_label in pbw_labels[left_index:]:
            bracket = _bracket(
                realizations[left_label],
                realizations[right_label],
                parity[left_label],
                parity[right_label],
                token_order,
            )
            for output_label, coefficient in _decompose(bracket, pivots).items():
                if coefficient:
                    structure_constants.append(
                        {
                            "X": left_label,
                            "Y": right_label,
                            "Z": output_label,
                            "coeff": _fraction_text(coefficient),
                            "sign_rule": "graded",
                        }
                    )

    boson_labels = [
        label
        for k in range(1, n + 1)
        for label in (f"b_{k}_p", f"b_{k}_m")
    ]
    realization_map = {
        label: _realization_entry(realizations[label], parity[label])
        for label in pbw_labels
    }
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
                "total": 2 * n * n + 5 * n + 1,
                "even": 2 * n * n + n + 1,
                "odd": 4 * n,
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
                "labels": boson_labels,
                "parity": 0,
                "description": "Bosonic oscillators b_k^+, b_k^- for k=1,...,n",
            },
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations for the standard pair",
                "relations": {
                    "conjugate_pair": "{a_1_m, a_1_p} = 1",
                    "same_type": "{a_1_p, a_1_p} = {a_1_m, a_1_m} = 0",
                },
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations for bosonic oscillators",
                "relations": {
                    "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
                    "conjugate_pair": "[b_i^-, b_j^+] = δ_ij",
                },
            },
            "mixed_commutators": {"boson_fermion": "[b_i^±, a_1^±] = 0"},
        },
        "central_elements": {
            "kappa": {
                "parity": 1,
                "central": True,
                "nilpotent": True,
                "relation": "kappa^2 = 0",
                "description": "Odd formal symbol for the inhomogeneous extension",
            },
            "K": {
                "parity": 0,
                "central": True,
                "relation": "K = 1",
                "description": "Even central identity; scalar identity, not an independent basis element",
            },
        },
        "basis": {
            "even": even,
            "odd": odd,
            "ordering_convention": "PBW: kappa < [odd by k, pp/pm/mp/mm] < [even: Cartan, positive roots, negative roots]; K=1 excluded",
        },
        "parity": {label: parity[label] for label in pbw_labels},
        "generator_realization": {
            "description": "Standard form with PBW oscillator ordering",
            "ordering": ", ".join(["a_1_p", "a_1_m", *boson_labels]),
            "realizations": realization_map,
        },
        "structure_constants": structure_constants,
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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--n",
        type=int,
        nargs="+",
        default=[1, 2, 3],
        help="bosonic ranks to generate (default: 1 2 3)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data"),
        help="output directory (default: data)",
    )
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for n in args.n:
        output = args.output_dir / f"C_{n}_structure.json"
        output.write_text(
            json.dumps(build_schema(n), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"Wrote {output}")


if __name__ == "__main__":
    main()
