#!/usr/bin/env python3
"""Generate Schema 1 structure data for C(n+1) = osp(2|2n)."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import TypeAlias

import sympy as sp


Word: TypeAlias = tuple[str, ...]
Polynomial: TypeAlias = dict[Word, sp.Rational]
Rational = sp.Rational
FERMION_P = "a_1_p"
FERMION_M = "a_1_m"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"


@dataclass(frozen=True)
class Generator:
    label: str
    parity: int
    polynomial: Polynomial
    frappat_form: str


def _oscillator_order(label: str) -> tuple[int, int, int]:
    if label == FERMION_P:
        return (0, 0, 0)
    if label == FERMION_M:
        return (0, 1, 0)
    family, index, sign = label.split("_")
    if family != "b" or sign not in {"p", "m"}:
        raise ValueError(f"Unknown oscillator label: {label}")
    return (1, int(index), 0 if sign == "p" else 1)


def _boson_parts(label: str) -> tuple[int, str]:
    family, index, sign = label.split("_")
    if family != "b" or sign not in {"p", "m"}:
        raise ValueError(f"Expected a boson label, got {label}")
    return int(index), sign


def _add_scaled(target: Polynomial, source: Polynomial, scale: sp.Rational) -> None:
    if not scale:
        return
    for word, coefficient in source.items():
        updated = target.get(word, sp.Rational(0)) + scale * coefficient
        if updated:
            target[word] = updated
        else:
            target.pop(word, None)


@lru_cache(maxsize=None)
def _normal_order_cached(word: Word) -> tuple[tuple[Word, sp.Rational], ...]:
    for index in range(len(word) - 1):
        left, right = word[index], word[index + 1]
        prefix, suffix = word[:index], word[index + 2 :]

        if left == right and left in {FERMION_P, FERMION_M}:
            return ()

        if left == FERMION_M and right == FERMION_P:
            result: Polynomial = {}
            _add_scaled(result, dict(_normal_order_cached(prefix + suffix)), sp.Rational(1))
            _add_scaled(
                result,
                dict(_normal_order_cached(prefix + (FERMION_P, FERMION_M) + suffix)),
                sp.Rational(-1),
            )
            return tuple(sorted(result.items()))

        if _oscillator_order(left) > _oscillator_order(right):
            result = {}
            swapped = prefix + (right, left) + suffix
            _add_scaled(result, dict(_normal_order_cached(swapped)), sp.Rational(1))

            if left.startswith("b_") and right.startswith("b_"):
                left_index, left_sign = _boson_parts(left)
                right_index, right_sign = _boson_parts(right)
                if left_sign == "m" and right_sign == "p" and left_index == right_index:
                    _add_scaled(
                        result,
                        dict(_normal_order_cached(prefix + suffix)),
                        sp.Rational(1),
                    )
            return tuple(sorted(result.items()))

    return ((word, sp.Rational(1)),)


def _normal_order(word: Word) -> Polynomial:
    return dict(_normal_order_cached(word))


def _word_polynomial(
    words: tuple[str, ...], coefficient: sp.Rational = sp.Rational(1)
) -> Polynomial:
    result: Polynomial = {}
    _add_scaled(result, _normal_order(words), coefficient)
    return result


def _add_polynomials(*polynomials: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for polynomial in polynomials:
        _add_scaled(result, polynomial, sp.Rational(1))
    return result


def _multiply_polynomials(left: Polynomial, right: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for left_word, left_coefficient in left.items():
        for right_word, right_coefficient in right.items():
            _add_scaled(
                result,
                _normal_order(left_word + right_word),
                left_coefficient * right_coefficient,
            )
    return result


def _subtract_polynomials(left: Polynomial, right: Polynomial) -> Polynomial:
    result = dict(left)
    _add_scaled(result, right, sp.Rational(-1))
    return result


def _graded_bracket(left: Generator, right: Generator) -> Polynomial:
    sign = -1 if left.parity and right.parity else 1
    return _subtract_polynomials(
        _multiply_polynomials(left.polynomial, right.polynomial),
        {
            word: sign * coefficient
            for word, coefficient in _multiply_polynomials(
                right.polynomial, left.polynomial
            ).items()
        },
    )


def _generator(
    label: str, parity: int, words: tuple[str, ...], frappat_form: str,
    coefficient: sp.Rational = sp.Rational(1),
) -> Generator:
    return Generator(label, parity, _word_polynomial(words, coefficient), frappat_form)


def _cartan_generator(
    label: str,
    terms: tuple[tuple[tuple[str, ...], sp.Rational], ...],
    frappat_form: str,
) -> Generator:
    polynomial: Polynomial = {}
    for words, coefficient in terms:
        _add_scaled(polynomial, _word_polynomial(words), coefficient)
    return Generator(label, 0, polynomial, frappat_form)


def _validate_rank(n: int) -> None:
    if n not in {1, 2, 3}:
        raise ValueError("This generator supports bosonic ranks n=1, 2, and 3.")


def build_generators(n: int) -> tuple[list[Generator], list[Generator]]:
    """Return the even and odd generators in their documented basis order."""
    _validate_rank(n)

    even = [
        _cartan_generator(
            "H_1",
            (
                ((FERMION_P, FERMION_M), sp.Rational(1)),
                (("b_1_p", "b_1_m"), sp.Rational(1)),
            ),
            "a_1^+ a_1^- + b_1^+ b_1^-",
        )
    ]
    for index in range(2, n + 1):
        even.append(
            _cartan_generator(
                f"H_{index}",
                (
                    ((f"b_{index - 1}_p", f"b_{index - 1}_m"), sp.Rational(1)),
                    ((f"b_{index}_p", f"b_{index}_m"), sp.Rational(-1)),
                ),
                f"b_{index - 1}^+ b_{index - 1}^- - b_{index}^+ b_{index}^-",
            )
        )
    even.append(
        _cartan_generator(
            f"H_{n + 1}",
            (
                ((f"b_{n}_p", f"b_{n}_m"), sp.Rational(-1)),
                ((), sp.Rational(-1, 2)),
            ),
            f"-b_{n}^+ b_{n}^- - 1/2",
        )
    )

    for index in range(1, n + 1):
        even.append(
            _generator(
                f"E_2del{index}_p",
                0,
                (f"b_{index}_p", f"b_{index}_p"),
                f"(b_{index}^+)^2",
            )
        )
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even.extend(
                (
                    _generator(
                        f"E_del{i}_del{j}_pp",
                        0,
                        (f"b_{i}_p", f"b_{j}_p"),
                        f"b_{i}^+ b_{j}^+",
                    ),
                    _generator(
                        f"E_del{i}_del{j}_pm",
                        0,
                        (f"b_{i}_p", f"b_{j}_m"),
                        f"b_{i}^+ b_{j}^-",
                    ),
                )
            )
    for index in range(1, n + 1):
        even.append(
            _generator(
                f"E_2del{index}_m",
                0,
                (f"b_{index}_m", f"b_{index}_m"),
                f"(b_{index}^-)^2",
            )
        )
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even.extend(
                (
                    _generator(
                        f"E_del{i}_del{j}_mp",
                        0,
                        (f"b_{i}_m", f"b_{j}_p"),
                        f"b_{i}^- b_{j}^+",
                    ),
                    _generator(
                        f"E_del{i}_del{j}_mm",
                        0,
                        (f"b_{i}_m", f"b_{j}_m"),
                        f"b_{i}^- b_{j}^-",
                    ),
                )
            )

    odd: list[Generator] = []
    for index in range(1, n + 1):
        odd.extend(
            (
                _generator(
                    f"E_eps1_del{index}_pp",
                    1,
                    (FERMION_P, f"b_{index}_p"),
                    f"a_1^+ b_{index}^+",
                ),
                _generator(
                    f"E_eps1_del{index}_pm",
                    1,
                    (FERMION_P, f"b_{index}_m"),
                    f"a_1^+ b_{index}^-",
                ),
                _generator(
                    f"E_eps1_del{index}_mp",
                    1,
                    (FERMION_M, f"b_{index}_p"),
                    f"a_1^- b_{index}^+",
                ),
                _generator(
                    f"E_eps1_del{index}_mm",
                    1,
                    (FERMION_M, f"b_{index}_m"),
                    f"a_1^- b_{index}^-",
                ),
            )
        )
    return even, odd


def _basis_decomposer(
    ordered_generators: list[Generator],
) -> tuple[list[Word], list[int], sp.Matrix]:
    monomials = sorted(
        {word for generator in ordered_generators for word in generator.polynomial}
    )
    matrix = sp.Matrix(
        [
            [generator.polynomial.get(word, sp.Rational(0)) for generator in ordered_generators]
            for word in monomials
        ]
    )
    _, pivot_rows = matrix.T.rref()
    if len(pivot_rows) != len(ordered_generators):
        raise ValueError("The oscillator realizations are not linearly independent.")
    square = matrix.extract(pivot_rows, range(len(ordered_generators)))
    return monomials, list(pivot_rows), square.inv()


def _decompose_in_basis(
    polynomial: Polynomial,
    ordered_generators: list[Generator],
    monomials: list[Word],
    pivot_rows: list[int],
    pivot_inverse: sp.Matrix,
) -> list[sp.Rational]:
    pivot_values = sp.Matrix(
        [polynomial.get(monomials[index], sp.Rational(0)) for index in pivot_rows]
    )
    coefficients = pivot_inverse * pivot_values
    reconstructed: Polynomial = {}
    for generator, coefficient in zip(ordered_generators, coefficients):
        _add_scaled(reconstructed, generator.polynomial, coefficient)
    if _subtract_polynomials(polynomial, reconstructed):
        raise ValueError("A graded bracket is not in the span of the declared basis.")
    return [sp.Rational(coefficient) for coefficient in coefficients]


def compute_structure_constants(n: int) -> list[dict[str, str]]:
    """Compute all nonzero ordered-pair graded brackets for bosonic rank n."""
    even, odd = build_generators(n)
    ordered_generators = odd + even
    monomials, pivot_rows, pivot_inverse = _basis_decomposer(ordered_generators)
    records: list[dict[str, str]] = []

    for left in ordered_generators:
        for right in ordered_generators:
            bracket = _graded_bracket(left, right)
            if not bracket:
                continue
            coefficients = _decompose_in_basis(
                bracket,
                ordered_generators,
                monomials,
                pivot_rows,
                pivot_inverse,
            )
            for result, coefficient in zip(ordered_generators, coefficients):
                if coefficient:
                    records.append(
                        {
                            "X": left.label,
                            "Y": right.label,
                            "Z": result.label,
                            "coeff": str(coefficient),
                            "sign_rule": "graded",
                        }
                    )
    return records


def _standard_form(polynomial: Polynomial) -> list[dict[str, object]]:
    terms: list[dict[str, object]] = []
    for word, coefficient in sorted(polynomial.items()):
        terms.append({"words": list(word), "coeff": str(coefficient)})
    return terms


def build_schema(n: int, generation_date: str | None = None) -> dict[str, object]:
    """Build a complete Schema 1 object without writing it to disk."""
    _validate_rank(n)
    even, odd = build_generators(n)
    ordered_generators = odd + even
    even_basis = [generator.label for generator in even]
    odd_basis = [generator.label for generator in odd]
    parity = {generator.label: generator.parity for generator in ordered_generators}
    realizations = {
        generator.label: {
            "standard_form": _standard_form(generator.polynomial),
            "frappat_form": generator.frappat_form,
            "parity": generator.parity,
        }
        for generator in ordered_generators
    }

    even_dimension = 2 * n * n + n + 1
    odd_dimension = 4 * n
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
                "total": even_dimension + odd_dimension,
                "even": even_dimension,
                "odd": odd_dimension,
                "formulas": {
                    "even": "2n^2+n+1",
                    "odd": "4n",
                    "total": "2n^2+5n+1",
                },
            },
        },
        "oscillator_generators": {
            "fermions": {
                "m": 1,
                "count": 2,
                "labels": [FERMION_P, FERMION_M],
                "parity": 1,
                "description": "Standard fermionic pair a_1^+, a_1^-.",
            },
            "bosons": {
                "n": n,
                "count": 2 * n,
                "labels": [
                    label
                    for index in range(1, n + 1)
                    for label in (f"b_{index}_p", f"b_{index}_m")
                ],
                "parity": 0,
                "description": "Bosonic oscillators b_k^± for k=1,...,n.",
            },
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations for the standard fermionic pair.",
                "relations": {
                    "conjugate_pair": "{a_1_m, a_1_p} = 1",
                    "same_type": "{a_1_p, a_1_p} = {a_1_m, a_1_m} = 0",
                },
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations for bosonic oscillators.",
                "relations": {
                    "same_type": "[b_i^±, b_j^±] = 0 for all i,j",
                    "conjugate_pair": "[b_i^-, b_j^+] = δ_ij",
                },
            },
            "mixed_commutators": {
                "boson_fermion": "[b_i^±, a_1^±] = 0 for all i."
            },
        },
        "central_elements": {
            "kappa": {
                "label": "κ",
                "parity": 1,
                "central": True,
                "nilpotent": True,
                "description": "Odd central symbol for the inhomogeneous extension.",
            },
            "K": {
                "label": "K",
                "parity": 0,
                "central": True,
                "identification": "1",
                "independent_basis_element": False,
                "description": "Even central identity, identified with the scalar 1.",
            },
        },
        "basis": {
            "even": even_basis,
            "odd": odd_basis,
            "ordering_convention": (
                "PBW: [odd in listed order] < [even in listed order]; "
                "K and κ are excluded."
            ),
        },
        "parity": parity,
        "generator_realization": {
            "description": "Standard oscillator form using the documented word ordering.",
            "ordering": ", ".join(
                [FERMION_P, FERMION_M]
                + [
                    label
                    for index in range(1, n + 1)
                    for label in (f"b_{index}_p", f"b_{index}_m")
                ]
            ),
            "realizations": realizations,
        },
        "structure_constants": compute_structure_constants(n),
        "metadata": {
            "generated_by": "build_C_structure_constants.py",
            "generation_date": generation_date or date.today().isoformat(),
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "Bakalov and Sullivan (2017)",
                "docs/math/Cn1_definition.md",
            ],
        },
    }


def output_path(n: int, data_dir: Path | None = None) -> Path:
    """Return the approved output path without creating the file."""
    _validate_rank(n)
    return (data_dir or DATA_DIR) / f"C_{n}_structure.json"


def write_schema(n: int, data_dir: Path | None = None) -> Path:
    """Write one generated Schema 1 file and return its path."""
    schema = build_schema(n)
    path = output_path(n, data_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "n",
        type=int,
        nargs="*",
        default=[1, 2, 3],
        help="Bosonic rank(s) to generate (default: 1 2 3).",
    )
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    args = parser.parse_args()
    for rank in args.n:
        print(write_schema(rank, args.data_dir))


if __name__ == "__main__":
    main()
