"""Build C(n+1) structure schemas from the oscillator realization."""

from __future__ import annotations

import argparse
import json
from datetime import date
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Iterable

Word = tuple[str, ...]
Polynomial = dict[Word, Fraction]
ROOT = Path(__file__).resolve().parents[1]
SUFFIXES = ("pp", "pm", "mp", "mm")


def _coefficient(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _basis(n: int) -> tuple[list[str], list[str]]:
    even = [f"H_{i}" for i in range(1, n + 2)]
    even.extend(f"E_2del{i}_p" for i in range(1, n + 1))
    even.extend(
        f"E_del{i}_del{j}_{suffix}"
        for i in range(1, n + 1)
        for j in range(i + 1, n + 1)
        for suffix in ("pp", "pm")
    )
    even.extend(f"E_2del{i}_m" for i in range(1, n + 1))
    even.extend(
        f"E_del{i}_del{j}_{suffix}"
        for i in range(1, n + 1)
        for j in range(i + 1, n + 1)
        for suffix in ("mm", "mp")
    )
    odd = [f"E_eps1_del{k}_{suffix}" for k in range(1, n + 1) for suffix in SUFFIXES]
    return even, odd


def _realizations(n: int) -> dict[str, Polynomial]:
    forms: dict[str, Polynomial] = {}

    def add(label: str, terms: Iterable[tuple[Fraction, Word]]) -> None:
        polynomial: Polynomial = {}
        for coefficient, word in terms:
            polynomial[word] = polynomial.get(word, Fraction(0)) + coefficient
        forms[label] = {word: coeff for word, coeff in polynomial.items() if coeff}

    add("H_1", [(Fraction(1), ("a_1_p", "a_1_m")), (Fraction(1), ("b_1_p", "b_1_m"))])
    for k in range(2, n + 1):
        add(
            f"H_{k}",
            [
                (Fraction(1), (f"b_{k - 1}_p", f"b_{k - 1}_m")),
                (Fraction(-1), (f"b_{k}_p", f"b_{k}_m")),
            ],
        )
    add(
        f"H_{n + 1}",
        [(Fraction(-1), (f"b_{n}_p", f"b_{n}_m")), (Fraction(-1, 2), ())],
    )
    for k in range(1, n + 1):
        add(f"E_2del{k}_p", [(Fraction(1), (f"b_{k}_p", f"b_{k}_p"))])
        add(f"E_2del{k}_m", [(Fraction(1), (f"b_{k}_m", f"b_{k}_m"))])
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            for suffix, signs in (("pp", ("p", "p")), ("pm", ("p", "m")),
                                  ("mp", ("m", "p")), ("mm", ("m", "m"))):
                add(
                    f"E_del{i}_del{j}_{suffix}",
                    [(Fraction(1), (f"b_{i}_{signs[0]}", f"b_{j}_{signs[1]}"))],
                )
    for k in range(1, n + 1):
        for suffix, f_sign, b_sign in (
            ("pp", "p", "p"), ("pm", "p", "m"),
            ("mp", "m", "p"), ("mm", "m", "m"),
        ):
            add(
                f"E_eps1_del{k}_{suffix}",
                [(Fraction(1), (f"a_1_{f_sign}", f"b_{k}_{b_sign}"))],
            )
    return forms


def _oscillator_order(n: int) -> list[str]:
    return ["a_1_p", "a_1_m"] + [
        f"b_{k}_{sign}" for k in range(1, n + 1) for sign in ("p", "m")
    ]


def _normalizer(n: int):
    order = {name: index for index, name in enumerate(_oscillator_order(n))}

    @lru_cache(maxsize=None)
    def normalize(word: Word) -> tuple[tuple[Word, Fraction], ...]:
        for i in range(len(word) - 1):
            left, right = word[i], word[i + 1]
            prefix, suffix = word[:i], word[i + 2 :]
            if left in ("a_1_p", "a_1_m") and right == left:
                return ()
            if left == "a_1_m" and right == "a_1_p":
                reordered = prefix + (right, left) + suffix
                removed = prefix + suffix
                return _combine(
                    (normalize(reordered), Fraction(-1)),
                    (normalize(removed), Fraction(1)),
                )
            if left.startswith("b_") and right.startswith("b_"):
                lk, ls = left[2:].split("_")
                rk, rs = right[2:].split("_")
                if lk == rk and ls == "m" and rs == "p":
                    reordered = prefix + (right, left) + suffix
                    removed = prefix + suffix
                    return _combine(
                        (normalize(reordered), Fraction(1)),
                        (normalize(removed), Fraction(1)),
                    )
            if order[left] > order[right]:
                return normalize(prefix + (right, left) + suffix)
        return ((word, Fraction(1)),)

    return normalize


def _combine(*terms: tuple[tuple[tuple[Word, Fraction], ...], Fraction]):
    combined: dict[Word, Fraction] = {}
    for polynomial, scale in terms:
        for word, coefficient in polynomial:
            combined[word] = combined.get(word, Fraction(0)) + scale * coefficient
    return tuple((word, coefficient) for word, coefficient in combined.items() if coefficient)


def _multiply(left: Polynomial, right: Polynomial, normalize) -> Polynomial:
    result: Polynomial = {}
    for left_word, left_coeff in left.items():
        for right_word, right_coeff in right.items():
            for word, coefficient in normalize(left_word + right_word):
                result[word] = result.get(word, Fraction(0)) + left_coeff * right_coeff * coefficient
    return {word: coefficient for word, coefficient in result.items() if coefficient}


def _bracket(left: Polynomial, right: Polynomial, left_parity: int, right_parity: int, normalize) -> Polynomial:
    forward = _multiply(left, right, normalize)
    backward = _multiply(right, left, normalize)
    result = dict(forward)
    sign = -1 if left_parity * right_parity % 2 == 0 else 1
    for word, coefficient in backward.items():
        result[word] = result.get(word, Fraction(0)) + sign * coefficient
    return {word: coefficient for word, coefficient in result.items() if coefficient}


def _span_coordinates(forms: dict[str, Polynomial], labels: list[str]):
    pivots: list[tuple[Word, Polynomial, dict[str, Fraction]]] = []
    pivot_words: set[Word] = set()
    for label in labels:
        vector = dict(forms[label])
        expression = {label: Fraction(1)}
        for pivot_word, pivot_vector, pivot_expression in pivots:
            factor = vector.get(pivot_word, Fraction(0))
            if not factor:
                continue
            for word, coefficient in pivot_vector.items():
                vector[word] = vector.get(word, Fraction(0)) - factor * coefficient
                if not vector[word]:
                    del vector[word]
            for basis_label, coefficient in pivot_expression.items():
                expression[basis_label] = expression.get(basis_label, Fraction(0)) - factor * coefficient
                if not expression[basis_label]:
                    del expression[basis_label]
        candidates = sorted(set(vector) - pivot_words)
        if not candidates:
            raise ValueError(f"Realization {label} is linearly dependent on the basis")
        pivot_word = candidates[0]
        scale = vector[pivot_word]
        vector = {word: coefficient / scale for word, coefficient in vector.items()}
        expression = {name: coefficient / scale for name, coefficient in expression.items()}
        pivots.append((pivot_word, vector, expression))
        pivot_words.add(pivot_word)

    def coordinates(vector: Polynomial) -> dict[str, Fraction]:
        expression: dict[str, Fraction] = {}
        for pivot_word, pivot_vector, pivot_expression in pivots:
            factor = vector.get(pivot_word, Fraction(0))
            if not factor:
                continue
            for word, coefficient in pivot_vector.items():
                vector[word] = vector.get(word, Fraction(0)) - factor * coefficient
                if not vector[word]:
                    del vector[word]
            for label, coefficient in pivot_expression.items():
                expression[label] = expression.get(label, Fraction(0)) + factor * coefficient
                if not expression[label]:
                    del expression[label]
        if vector:
            raise ValueError(f"Bracket is outside the generator span: {vector}")
        return expression

    return coordinates


def _realization_json(label: str, polynomial: Polynomial, parity: int) -> dict:
    display_terms: list[str] = []
    terms = [
        {"words": list(word), "coeff": _coefficient(coefficient)}
        for word, coefficient in sorted(polynomial.items())
    ]
    for word, coefficient in sorted(polynomial.items()):
        oscillator_word = " ".join(
            token.replace("_p", "^+").replace("_m", "^-") for token in word
        ) or "1"
        magnitude = _coefficient(abs(coefficient))
        term = oscillator_word if magnitude == "1" else f"{magnitude} {oscillator_word}"
        if not display_terms:
            display_terms.append(f"-{term}" if coefficient < 0 else term)
        else:
            display_terms.append(f" - {term}" if coefficient < 0 else f" + {term}")
    return {
        "standard_form": terms,
        "frappat_form": "".join(display_terms),
        "parity": parity,
    }


def build_schema(n: int) -> dict:
    if n < 1:
        raise ValueError("Bosonic rank n must be at least 1")
    even, odd = _basis(n)
    labels = odd + even
    parity = {label: 0 for label in even} | {label: 1 for label in odd}
    forms = _realizations(n)
    normalize = _normalizer(n)
    coordinates = _span_coordinates(forms, labels)
    constants = []
    for left_index, left_label in enumerate(labels):
        for right_index in range(left_index, len(labels)):
            right_label = labels[right_index]
            result = _bracket(
                forms[left_label], forms[right_label],
                parity[left_label], parity[right_label], normalize,
            )
            for output, coefficient in sorted(coordinates(result).items()):
                constants.append({
                    "X": left_label,
                    "Y": right_label,
                    "Z": output,
                    "coeff": _coefficient(coefficient),
                    "sign_rule": "graded",
                })

    dimension_even = 2 * n * n + n + 1
    dimension_odd = 4 * n
    alternative_osp = f"osp(2|{2 * n})"
    realizations = {
        label: _realization_json(label, forms[label], parity[label])
        for label in labels
    }
    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n + 1})",
            "alternative_notation": {
                "osp": alternative_osp,
                "dimension_formula": "osp(2m|2n) with m=1",
            },
            "dimension": {
                "total": dimension_even + dimension_odd,
                "even": dimension_even,
                "odd": dimension_odd,
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
                "rank": n,
                "count": 2 * n,
                "labels": [f"b_{k}_{s}" for k in range(1, n + 1) for s in ("p", "m")],
                "parity": 0,
                "description": "Bosonic oscillators b_k^+, b_k^- for k=1,...,n",
            },
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relation",
                "relations": {
                    "conjugate_pair": "{a_1_m, a_1_p} = 1",
                    "same_type": "{a_1_p, a_1_p} = {a_1_m, a_1_m} = 0",
                },
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations",
                "relations": {
                    "same_type": "[b_i^±, b_j^±] = 0",
                    "conjugate_pair": "[b_i^-, b_j^+] = δ_ij",
                },
            },
            "mixed_commutators": {"fermion_boson": "[a_1^±, b_j^±] = 0"},
        },
        "central_elements": {
            "kappa": {
                "parity": 1,
                "central": True,
                "nilpotent": True,
                "relation": "kappa^2 = 0",
                "description": "Formal odd central symbol for the inhomogeneous extension",
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
            "ordering_convention": "PBW: odd generators in listed order < even generators in listed order; kappa precedes both blocks when used; K=1 excluded",
        },
        "parity": parity,
        "generator_realization": {
            "description": "Standard oscillator form with exact rational coefficients",
            "ordering": _oscillator_order(n),
            "realizations": realizations,
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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ranks", type=int, nargs="+", default=[1, 2, 3])
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for n in args.ranks:
        schema = build_schema(n)
        path = args.output_dir / f"C_{n}_structure.json"
        path.write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Wrote {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}")


if __name__ == "__main__":
    main()
