"""Generate Schema 2 gamma data from the C(n+1) oscillator relations."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import date
from functools import lru_cache
from pathlib import Path

import sympy as sp

from C_generators import (
    _add,
    _normalizer,
    _ordered_basis,
    _realizations,
)


def _deformed_normalizer(n: int):
    base_normalize = _normalizer(n)
    ordering = {label: i for i, label in enumerate(
        ("a_1_p", "a_1_m") + tuple(
            f"b_{k}_{sign}" for k in range(1, n + 1) for sign in ("p", "m")
        )
    )}

    def pack(base, corrections):
        return (
            tuple(sorted((word, sp.Rational(coeff)) for word, coeff in base.items() if coeff)),
            tuple(
                (parameter, tuple(sorted(
                    (word, sp.Rational(coeff)) for word, coeff in polynomial.items() if coeff
                )))
                for parameter, polynomial in sorted(corrections.items())
                if any(polynomial.values())
            ),
        )

    @lru_cache(maxsize=None)
    def normalize(word):
        for index in range(len(word) - 1):
            left, right = word[index], word[index + 1]
            if ordering[left] <= ordering[right]:
                continue
            prefix, suffix = word[:index], word[index + 2 :]
            swapped = prefix + (right, left) + suffix

            if (left, right) == ("a_1_m", "a_1_p"):
                base_one, corrections_one = normalize(prefix + suffix)
                base_two, corrections_two = normalize(swapped)
                base = Counter(dict(base_one))
                for key, coefficient in base_two:
                    base[key] -= coefficient
                corrections = {}
                for parameter, polynomial in corrections_one:
                    target = corrections.setdefault(parameter, Counter())
                    for key, coefficient in polynomial:
                        target[key] += coefficient
                for parameter, polynomial in corrections_two:
                    target = corrections.setdefault(parameter, Counter())
                    for key, coefficient in polynomial:
                        target[key] -= coefficient
            elif left.startswith("b_") and right.startswith("b_"):
                left_index, left_sign = left.rsplit("_", 1)
                right_index, right_sign = right.rsplit("_", 1)
                if left_index == right_index and (left_sign, right_sign) == ("m", "p"):
                    base_one, corrections_one = normalize(swapped)
                    base_two, corrections_two = normalize(prefix + suffix)
                    base = Counter(dict(base_one))
                    for key, coefficient in base_two:
                        base[key] += coefficient
                    corrections = {}
                    for parameter, polynomial in corrections_one + corrections_two:
                        target = corrections.setdefault(parameter, Counter())
                        for key, coefficient in polynomial:
                            target[key] += coefficient
                else:
                    base, corrections = normalize(swapped)
                    base = dict(base)
                    corrections = {parameter: dict(poly) for parameter, poly in corrections}
            elif left.startswith("b_") and right.startswith("a_1_"):
                base, corrections = normalize(swapped)
                base = dict(base)
                corrections = {parameter: dict(poly) for parameter, poly in corrections}
                parameter = f"gb_{right}_{left}"
                for canonical, coefficient in base_normalize(prefix + suffix):
                    target = corrections.setdefault(parameter, {})
                    target[canonical] = target.get(canonical, sp.Rational(0)) + coefficient
            else:
                base, corrections = normalize(swapped)
                base = dict(base)
                corrections = {parameter: dict(poly) for parameter, poly in corrections}

            return pack(base, corrections)

        fermions = [label for label in word if label.startswith("a_1_")]
        if len(fermions) != len(set(fermions)):
            return pack({}, {})
        return pack({word: sp.Rational(1)}, {})

    def expand(word):
        base, corrections = normalize(word)
        return dict(base), {
            parameter: dict(polynomial) for parameter, polynomial in corrections
        }

    return expand, base_normalize


def _add_corrections(target, source, scale=sp.Rational(1)):
    for parameter, polynomial in source.items():
        target[parameter] = _add(target.get(parameter, {}), polynomial, scale)


def _multiply_deformed(left, right, normalize):
    base: dict[tuple[str, ...], sp.Rational] = {}
    corrections: dict[str, dict[tuple[str, ...], sp.Rational]] = {}
    for left_word, left_coeff in left.items():
        for right_word, right_coeff in right.items():
            base_part, correction_part = normalize(left_word + right_word)
            factor = left_coeff * right_coeff
            base = _add(base, base_part, factor)
            _add_corrections(corrections, correction_part, factor)
    return base, corrections


def _bracket_deformed(left, right, left_parity, right_parity, normalize):
    xy_base, xy_corrections = _multiply_deformed(left, right, normalize)
    yx_base, yx_corrections = _multiply_deformed(right, left, normalize)
    sign = -1 if left_parity * right_parity % 2 else 1
    base = _add(xy_base, yx_base, -sign)
    _add_corrections(xy_corrections, yx_corrections, -sign)
    return base, xy_corrections


def _project(polynomial, basis, realizations, pivot_rows, inverse, monomials):
    vector = sp.Matrix([polynomial.get(monomials[row], 0) for row in pivot_rows])
    coefficients = inverse * vector
    reconstructed = {}
    for index, coefficient in enumerate(coefficients):
        if coefficient:
            reconstructed = _add(reconstructed, realizations[basis[index]], coefficient)
    if reconstructed != polynomial:
        raise ValueError("deformation bracket is not in the declared Schema 1 basis")
    return coefficients


def build_gamma_schema(n: int) -> dict:
    if n < 1:
        raise ValueError("bosonic rank n must be a positive integer")
    normalize, base_normalize = _deformed_normalizer(n)
    even_basis, odd_basis = _ordered_basis(n)
    basis = even_basis + odd_basis
    realizations, parity = _realizations(n, base_normalize)
    gamma_basis = basis + ["K"]
    gamma_realizations = {**realizations, "K": {(): sp.Rational(1)}}
    monomials = sorted({word for label in gamma_basis for word in gamma_realizations[label]})
    basis_matrix = sp.Matrix([
        [gamma_realizations[label].get(word, sp.Rational(0)) for label in gamma_basis]
        for word in monomials
    ])
    _, pivot_rows = basis_matrix.T.rref()
    pivot_rows = list(pivot_rows)
    inverse = basis_matrix[pivot_rows, :].inv()

    parameters = [
        f"gb_a_1_{fermion_sign}_b_{k}_{boson_sign}"
        for fermion_sign in ("p", "m")
        for k in range(1, n + 1)
        for boson_sign in ("p", "m")
    ]
    gamma_terms = []
    for x in basis:
        for y in basis:
            _, corrections = _bracket_deformed(
                realizations[x], realizations[y], parity[x], parity[y], normalize
            )
            for parameter, polynomial in corrections.items():
                if not polynomial:
                    continue
                try:
                    coefficients = _project(
                        polynomial, gamma_basis, gamma_realizations,
                        pivot_rows, inverse, monomials
                    )
                except ValueError as error:
                    raise ValueError(
                        f"deformed bracket [{x}, {y}] for {parameter} is not closed: "
                        f"{polynomial}"
                    ) from error
                for z, coefficient in zip(gamma_basis, coefficients):
                    if coefficient:
                        gamma_terms.append({
                            "X": x,
                            "Y": y,
                            "Z": z,
                            "parameter": parameter,
                            "coeff": str(coefficient),
                            "sign_rule": "graded",
                        })

    gb_matrix = [
        [
            f"gb_a_1_{fermion_sign}_b_{k}_{boson_sign}"
            for k in range(1, n + 1)
            for boson_sign in ("p", "m")
        ]
        for fermion_sign in ("p", "m")
    ]
    off_basis_terms = [term for term in gamma_terms if term["Z"] == "K"]
    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n + 1})",
        },
        "gb_matrix": {
            "rows": ["a_1_p", "a_1_m"],
            "columns": [
                label
                for k in range(1, n + 1)
                for label in (f"b_{k}_p", f"b_{k}_m")
            ],
            "entries": gb_matrix,
            "parameter_parity": 1,
        },
        "inhomogeneous_deformation": {
            "central_parameter": "kappa",
            "bracket_formula": "[X,Y]_gamma = [X,Y]_0 + kappa * gamma(X,Y)",
            "exchange_relations": [
                {
                    "X": f"b_{k}_{boson_sign}",
                    "Y": f"a_1_{fermion_sign}",
                    "relation": (
                        f"[b_{k}_{boson_sign}, a_1_{fermion_sign}] = "
                        f"-{gb_matrix[0 if fermion_sign == 'p' else 1][2 * (k - 1) + (0 if boson_sign == 'p' else 1)]} * kappa"
                    ),
                }
                for fermion_sign in ("p", "m")
                for k in range(1, n + 1)
                for boson_sign in ("p", "m")
            ],
            "parameters": [
                {
                    "label": parameter,
                    "fermion": f"a_1_{parameter.split('_')[3]}",
                    "boson": f"b_{parameter.split('_')[5]}_{parameter.split('_')[6]}",
                    "parity": 1,
                }
                for parameter in parameters
            ],
            "gamma_coefficients": gamma_terms,
            "gamma_convention": (
                "Each record contributes coeff * parameter * Z to gamma(X,Y); "
                "kappa is factored to the left."
            ),
            "consistency": {
                "schema1_closed": not off_basis_terms,
                "off_basis_terms": off_basis_terms,
                "grading_consistent": False,
                "grading_note": (
                    "The supplied relation has odd gb parameters and odd kappa, so "
                    "gb*kappa is even although [b,a] is odd."
                ),
            },
        },
        "schema1_reference": f"C_{n}_structure.json",
        "metadata": {
            "generated_by": "src/C_gamma.py",
            "generation_date": date.today().isoformat(),
            "references": ["docs/math/C_inhomogeneous_definition.md"],
        },
    }


def generate_all(output_dir: Path, ranks=(1, 2, 3)) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for n in ranks:
        path = output_dir / f"C_{n}_gamma.json"
        path.write_text(json.dumps(build_gamma_schema(n), indent=2, ensure_ascii=False) + "\n")
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
