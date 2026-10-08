"""Generate Schema 1 data for C(n+1) from its oscillator realization."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import date
from functools import lru_cache
from pathlib import Path

import sympy as sp


Scalar = sp.Rational
Polynomial = dict[tuple[str, ...], sp.Rational]


def _oscillator_order(n: int) -> tuple[str, ...]:
    return ("a_1_p", "a_1_m") + tuple(
        f"b_{k}_{sign}" for k in range(1, n + 1) for sign in ("p", "m")
    )


def _normalizer(n: int):
    order = {label: index for index, label in enumerate(_oscillator_order(n))}

    @lru_cache(maxsize=None)
    def normalize(word: tuple[str, ...]) -> tuple[tuple[tuple[str, ...], sp.Rational], ...]:
        for index in range(len(word) - 1):
            left, right = word[index], word[index + 1]
            if order[left] <= order[right]:
                continue
            prefix, suffix = word[:index], word[index + 2 :]

            if (left, right) == ("a_1_m", "a_1_p"):
                terms = Counter(dict(normalize(prefix + suffix)))
                for canonical, coeff in normalize(prefix + (right, left) + suffix):
                    terms[canonical] -= coeff
            elif left.startswith("b_") and right.startswith("b_"):
                left_index, left_sign = left.rsplit("_", 1)
                right_index, right_sign = right.rsplit("_", 1)
                if left_index == right_index and (left_sign, right_sign) == ("m", "p"):
                    terms = Counter()
                    for canonical, coeff in normalize(prefix + (right, left) + suffix):
                        terms[canonical] += coeff
                    for canonical, coeff in normalize(prefix + suffix):
                        terms[canonical] += coeff
                else:
                    terms = Counter()
                    for canonical, coeff in normalize(prefix + (right, left) + suffix):
                        terms[canonical] += coeff
            else:
                terms = Counter()
                for canonical, coeff in normalize(prefix + (right, left) + suffix):
                    terms[canonical] += coeff
            return tuple(sorted((key, sp.Rational(value)) for key, value in terms.items() if value))
        fermions = [label for label in word if label.startswith("a_1_")]
        if len(fermions) != len(set(fermions)):
            return ()
        return ((word, sp.Rational(1)),)

    return normalize


def _add(left: Polynomial, right: Polynomial, scale=sp.Rational(1)) -> Polynomial:
    result = left.copy()
    for word, coeff in right.items():
        result[word] = result.get(word, sp.Rational(0)) + scale * coeff
        if result[word] == 0:
            del result[word]
    return result


def _multiply(left: Polynomial, right: Polynomial, normalize) -> Polynomial:
    result: Polynomial = {}
    for left_word, left_coeff in left.items():
        for right_word, right_coeff in right.items():
            for word, coeff in normalize(left_word + right_word):
                result[word] = result.get(word, sp.Rational(0)) + left_coeff * right_coeff * coeff
    return {word: coeff for word, coeff in result.items() if coeff}


def _word(*labels: str) -> Polynomial:
    return {tuple(labels): sp.Rational(1)}


def _realizations(n: int, normalize):
    realizations: dict[str, Polynomial] = {}
    parities: dict[str, int] = {}

    def put(label: str, polynomial: Polynomial, parity: int) -> None:
        realizations[label] = polynomial
        parities[label] = parity

    for k in range(1, n + 1):
        put(f"H_{k}", {}, 0)
    put(f"H_{n + 1}", {}, 0)
    if n == 1:
        put("H_1", _add(_word("a_1_p", "a_1_m"), _word("b_1_p", "b_1_m")), 0)
    else:
        put("H_1", _add(_word("a_1_p", "a_1_m"), _word("b_1_p", "b_1_m")), 0)
        for k in range(2, n + 1):
            put(
                f"H_{k}",
                _add(_word(f"b_{k - 1}_p", f"b_{k - 1}_m"),
                     _word(f"b_{k}_p", f"b_{k}_m"), -1),
                0,
            )
    put(
        f"H_{n + 1}",
        _add({}, _word(f"b_{n}_p", f"b_{n}_m"), -1),
        0,
    )
    realizations[f"H_{n + 1}"][()] = sp.Rational(-1, 2)

    for k in range(1, n + 1):
        put(f"E_2del{k}_p", { (f"b_{k}_p", f"b_{k}_p"): sp.Rational(1, 2) }, 0)
        put(f"E_2del{k}_m", { (f"b_{k}_m", f"b_{k}_m"): sp.Rational(1, 2) }, 0)
        for suffix, fermion, boson_sign in (
            ("pp", "a_1_p", "p"),
            ("pm", "a_1_p", "m"),
            ("mp", "a_1_m", "p"),
            ("mm", "a_1_m", "m"),
        ):
            put(
                f"E_eps1_del{k}_{suffix}",
                _word(fermion, f"b_{k}_{boson_sign}"),
                1,
            )

    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            for suffix, signs in (
                ("pp", ("p", "p")),
                ("pm", ("p", "m")),
                ("mm", ("m", "m")),
                ("mp", ("m", "p")),
            ):
                put(
                    f"E_del{i}_del{j}_{suffix}",
                    _word(f"b_{i}_{signs[0]}", f"b_{j}_{signs[1]}"),
                    0,
                )
    return realizations, parities


def _ordered_basis(n: int) -> tuple[list[str], list[str]]:
    even = [f"H_{k}" for k in range(1, n + 2)]
    even.extend(f"E_2del{k}_p" for k in range(1, n + 1))
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even.extend((f"E_del{i}_del{j}_pp", f"E_del{i}_del{j}_pm"))
    even.extend(f"E_2del{k}_m" for k in range(1, n + 1))
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even.extend((f"E_del{i}_del{j}_mm", f"E_del{i}_del{j}_mp"))
    odd = [
        f"E_eps1_del{k}_{suffix}"
        for k in range(1, n + 1)
        for suffix in ("pp", "pm", "mp", "mm")
    ]
    return even, odd


def _poly_bracket(
    left: Polynomial, right: Polynomial, left_parity: int, right_parity: int, normalize
) -> Polynomial:
    product_xy = _multiply(left, right, normalize)
    product_yx = _multiply(right, left, normalize)
    sign = -1 if left_parity * right_parity % 2 else 1
    return _add(product_xy, product_yx, -sign)


def _structure_constants(basis, realizations, parities, normalize):
    monomials = sorted({word for label in basis for word in realizations[label]})
    matrix = sp.Matrix([
        [realizations[label].get(word, sp.Rational(0)) for label in basis]
        for word in monomials
    ])
    _, pivots = matrix.T.rref()
    pivot_rows = list(pivots)
    square = matrix[pivot_rows, :]
    inverse = square.inv()
    rows_by_word = {word: index for index, word in enumerate(monomials)}
    constants = []

    for x_index, x in enumerate(basis):
        for y in basis:
            bracket = _poly_bracket(
                realizations[x], realizations[y], parities[x], parities[y], normalize
            )
            if not bracket:
                continue
            vector = sp.Matrix([bracket.get(monomials[row], 0) for row in pivot_rows])
            coefficients = inverse * vector
            reconstructed: Polynomial = {}
            for index, coefficient in enumerate(coefficients):
                if coefficient:
                    reconstructed = _add(
                        reconstructed,
                        realizations[basis[index]],
                        coefficient,
                    )
            if reconstructed != bracket:
                raise ValueError(f"Bracket [{x}, {y}] is not in the declared basis")
            for z, coefficient in zip(basis, coefficients):
                if coefficient:
                    constants.append({
                        "X": x,
                        "Y": y,
                        "Z": z,
                        "coeff": str(coefficient),
                        "sign_rule": "graded",
                    })
    return constants


def build_schema(n: int) -> dict:
    if n < 1:
        raise ValueError("bosonic rank n must be a positive integer")
    normalize = _normalizer(n)
    even_basis, odd_basis = _ordered_basis(n)
    basis = even_basis + odd_basis
    realizations, parities = _realizations(n, normalize)

    def terms(poly):
        return [
            {"words": list(word), "coeff": str(coeff)}
            for word, coeff in sorted(poly.items())
        ]

    output_realizations = {}
    for label in basis:
        form = realizations[label]
        output_realizations[label] = {
            "standard_form": terms(form),
            "frappat_form": " + ".join(
                f"{coeff}*{' '.join(word) if word else '1'}" for word, coeff in sorted(form.items())
            ),
            "parity": parities[label],
        }
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
                "description": "One standard fermionic creation/annihilation pair.",
            },
            "bosons": {
                "count": 2 * n,
                "n": n,
                "labels": list(_oscillator_order(n)[2:]),
                "description": "Bosonic oscillators b_k^± with k=1,...,n.",
            },
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations for a standard pair.",
                "relations": {
                    "conjugate_pair": "{a_1_m, a_1_p} = 1",
                    "same_type": "{a_1_p, a_1_p} = {a_1_m, a_1_m} = 0",
                },
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations for bosonic oscillators.",
                "relations": {
                    "same_type": "[b_i^±, b_j^±] = 0 for all i,j and each sign choice",
                    "conjugate_pair": "[b_i^-, b_j^+] = δ_ij",
                },
            },
            "mixed_commutators": {
                "description": "Fermions and bosons commute in the undeformed oscillator algebra.",
                "boson_fermion": "[b_i^±, a_1^±] = 0",
            },
        },
        "central_elements": {
            "kappa": {
                "parity": 1,
                "central": True,
                "nilpotent": True,
                "relation": "kappa^2 = 0",
                "description": "Formal odd central symbol for the nilpotent extension.",
            },
            "K": {
                "parity": 0,
                "central": True,
                "identity": True,
                "value": "1",
                "description": "Even central identity; identified with the scalar 1.",
            },
        },
        "basis": {
            "even": even_basis,
            "odd": odd_basis,
            "ordering_convention": "PBW: [odd generators] < [even generators]; kappa and K are excluded.",
        },
        "parity": {label: parities[label] for label in basis},
        "generator_realization": {
            "description": "Standard form with PBW ordering",
            "ordering": ", ".join(_oscillator_order(n)),
            "realizations": output_realizations,
        },
        "structure_constants": _structure_constants(basis, realizations, parities, normalize),
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": date.today().isoformat(),
            "references": [
                "docs/math/Cn1_definition.md",
                "docs/json_schema_specification.md",
            ],
        },
    }


def generate_all(output_dir: Path, ranks=(1, 2, 3)) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for n in ranks:
        path = output_dir / f"C_{n}_structure.json"
        path.write_text(json.dumps(build_schema(n), indent=2, ensure_ascii=False) + "\n")
        paths.append(path)
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("data"))
    parser.add_argument("--ranks", type=int, nargs="+", default=[1, 2, 3])
    args = parser.parse_args()
    for path in generate_all(args.output_dir, args.ranks):
        print(path)


if __name__ == "__main__":
    main()
