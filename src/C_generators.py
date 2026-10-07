#!/usr/bin/env python3
"""Generate exact Schema 1 structure data for C(n+1) = osp(2|2n)."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import date
from fractions import Fraction
from itertools import combinations
from math import comb
from pathlib import Path
from typing import TypeAlias


Monomial: TypeAlias = tuple[int, int, tuple[tuple[int, int], ...]]
Polynomial: TypeAlias = dict[Monomial, Fraction]

ORDERING_CONVENTION = (
    "PBW: [odd: epsilon-positive, epsilon-negative] < "
    "[even: Cartan, positive roots, negative roots]; K=1 is excluded"
)


def _clean(poly: Polynomial) -> Polynomial:
    return {monomial: coeff for monomial, coeff in poly.items() if coeff}


def _add_scaled(
    target: Polynomial, source: Polynomial, scale: Fraction
) -> None:
    if not scale:
        return
    for monomial, coeff in source.items():
        target[monomial] = target.get(monomial, Fraction()) + scale * coeff
        if not target[monomial]:
            del target[monomial]


def _fermion_normal_form(word: tuple[str, ...]) -> dict[tuple[str, ...], int]:
    """Reduce a fermion word to 1, a+, a-, or a+a- using the CAR."""
    for index, (left, right) in enumerate(zip(word, word[1:])):
        if left == right:
            return {}
        if left == "m" and right == "p":
            before = word[:index]
            after = word[index + 2 :]
            reduced = _fermion_normal_form(before + after)
            swapped = _fermion_normal_form(before + ("p", "m") + after)
            result = dict(reduced)
            for term, coeff in swapped.items():
                result[term] = result.get(term, 0) - coeff
                if not result[term]:
                    del result[term]
            return result
    return {word: 1}


def _boson_products(
    left: tuple[tuple[int, int], ...],
    right: tuple[tuple[int, int], ...],
) -> list[tuple[tuple[tuple[int, int], ...], int]]:
    products: list[tuple[tuple[tuple[int, int], ...], int]] = [((), 1)]
    for (left_p, left_m), (right_p, right_m) in zip(left, right):
        mode_products = []
        for contractions in range(min(left_m, right_p) + 1):
            factor = comb(left_m, contractions)
            for offset in range(contractions):
                factor *= right_p - offset
            mode_products.append(
                (
                    (
                        left_p + right_p - contractions,
                        left_m + right_m - contractions,
                    ),
                    factor,
                )
            )
        products = [
            (prefix + (mode,), prefix_factor * mode_factor)
            for prefix, prefix_factor in products
            for mode, mode_factor in mode_products
        ]
    return products


def _multiply_monomials(
    left: Monomial, right: Monomial
) -> dict[Monomial, int]:
    left_fermions = ("p",) * left[0] + ("m",) * left[1]
    right_fermions = ("p",) * right[0] + ("m",) * right[1]
    fermion_products = _fermion_normal_form(left_fermions + right_fermions)
    result: dict[Monomial, int] = {}
    for fermion_word, fermion_coeff in fermion_products.items():
        fermion_p = int("p" in fermion_word)
        fermion_m = int("m" in fermion_word)
        for bosons, boson_coeff in _boson_products(left[2], right[2]):
            monomial = (fermion_p, fermion_m, bosons)
            result[monomial] = result.get(monomial, 0) + (
                fermion_coeff * boson_coeff
            )
    return {monomial: coeff for monomial, coeff in result.items() if coeff}


def _multiply(left: Polynomial, right: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for left_monomial, left_coeff in left.items():
        for right_monomial, right_coeff in right.items():
            for monomial, coeff in _multiply_monomials(
                left_monomial, right_monomial
            ).items():
                result[monomial] = result.get(monomial, Fraction()) + (
                    left_coeff * right_coeff * coeff
                )
    return _clean(result)


def _empty_monomial(n: int) -> Monomial:
    return (0, 0, ((0, 0),) * n)


def _word_polynomial(words: list[str], n: int) -> Polynomial:
    result: Polynomial = {_empty_monomial(n): Fraction(1)}
    for word in words:
        if word == "a_1_p":
            factor: Polynomial = {(1, 0, ((0, 0),) * n): Fraction(1)}
        elif word == "a_1_m":
            factor = {(0, 1, ((0, 0),) * n): Fraction(1)}
        else:
            prefix, mode_index, sign = word.split("_")
            if prefix != "b" or sign not in ("p", "m"):
                raise ValueError(f"Unknown oscillator label: {word}")
            mode = int(mode_index) - 1
            if not 0 <= mode < n:
                raise ValueError(f"Oscillator index out of range: {word}")
            bosons = [(0, 0)] * n
            bosons[mode] = (1, 0) if sign == "p" else (0, 1)
            factor = {(0, 0, tuple(bosons)): Fraction(1)}
        result = _multiply(result, factor)
    return result


def _term(words: list[str], coeff: Fraction | int | str = 1) -> dict:
    return {"words": words, "coeff": _fraction_string(Fraction(coeff))}


def _fraction_string(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def build_basis(n: int) -> dict[str, list[str] | str]:
    """Build the finalized C(n+1) parity-block basis for bosonic rank n."""
    if n < 1:
        raise ValueError("n must be a positive integer")

    pairs = list(combinations(range(1, n + 1), 2))
    even = [f"H_{index}" for index in range(1, n + 2)]
    even.extend(f"E_2del{index}_p" for index in range(1, n + 1))
    even.extend(
        f"E_del{i}_del{j}_{suffix}"
        for i, j in pairs
        for suffix in ("pp", "pm")
    )
    even.extend(f"E_2del{index}_m" for index in range(1, n + 1))
    even.extend(
        f"E_del{i}_del{j}_{suffix}"
        for i, j in pairs
        for suffix in ("mm", "mp")
    )

    odd = [
        f"E_eps1_del{index}_{suffix}"
        for index in range(1, n + 1)
        for suffix in ("pp", "pm")
    ]
    odd.extend(
        f"E_eps1_del{index}_{suffix}"
        for index in range(1, n + 1)
        for suffix in ("mp", "mm")
    )
    return {
        "even": even,
        "odd": odd,
        "ordering_convention": ORDERING_CONVENTION,
    }


def _realization_terms(name: str, n: int) -> tuple[list[dict], str]:
    if name == "H_1":
        return [
            _term(["a_1_p", "a_1_m"]),
            _term(["b_1_p", "b_1_m"]),
        ], "a_1^+ a_1^- + b_1^+ b_1^-"
    if name.startswith("H_"):
        index = int(name[2:])
        if index == n + 1:
            return [
                _term([f"b_{n}_p", f"b_{n}_m"], -1),
                _term([], Fraction(-1, 2)),
            ], f"-b_{n}^+ b_{n}^- - 1/2"
        return [
            _term([f"b_{index - 1}_p", f"b_{index - 1}_m"]),
            _term([f"b_{index}_p", f"b_{index}_m"], -1),
        ], (
            f"b_{index - 1}^+ b_{index - 1}^- - "
            f"b_{index}^+ b_{index}^-"
        )

    if name.startswith("E_2del"):
        rest = name.removeprefix("E_2del")
        index = int(rest[:-2])
        sign = rest[-1]
        oscillator_sign = "p" if sign == "p" else "m"
        coeff = Fraction(1, 2) if index == n else Fraction(1)
        boson_sign = "+" if oscillator_sign == "p" else "-"
        coeff_text = "1/2 " if coeff == Fraction(1, 2) else ""
        return [
            _term([f"b_{index}_{oscillator_sign}"] * 2, coeff)
        ], f"{coeff_text}(b_{index}^{boson_sign})^2"

    if name.startswith("E_del"):
        _, first_label, second_label, suffix = name.split("_")
        first_index = int(first_label.removeprefix("del"))
        second_index = int(second_label.removeprefix("del"))
        signs = {"pp": ("p", "p"), "pm": ("p", "m"),
                 "mm": ("m", "m"), "mp": ("m", "p")}
        first_sign, second_sign = signs[suffix]
        first_symbol = "+" if first_sign == "p" else "-"
        second_symbol = "+" if second_sign == "p" else "-"
        return [
            _term(
                [
                    f"b_{first_index}_{first_sign}",
                    f"b_{second_index}_{second_sign}",
                ]
            )
        ], f"b_{first_index}^{first_symbol} b_{second_index}^{second_symbol}"

    if name.startswith("E_eps1_del"):
        rest = name.removeprefix("E_eps1_del")
        index = int(rest.split("_")[0])
        suffix = rest.split("_")[1]
        fermion_sign, boson_sign = suffix
        fermion_symbol = "+" if fermion_sign == "p" else "-"
        boson_symbol = "+" if boson_sign == "p" else "-"
        return [
            _term(
                [
                    f"a_1_{fermion_sign}",
                    f"b_{index}_{boson_sign}",
                ]
            )
        ], f"a_1^{fermion_symbol} b_{index}^{boson_symbol}"

    raise ValueError(f"Unknown generator label: {name}")


def build_realizations(n: int, basis: dict | None = None) -> dict[str, dict]:
    """Build exact oscillator polynomials and their Schema 1 representations."""
    basis = basis or build_basis(n)
    result = {}
    for parity, labels in ((0, basis["even"]), (1, basis["odd"])):
        for name in labels:
            terms, frappat_form = _realization_terms(name, n)
            polynomial: Polynomial = {}
            for entry in terms:
                coeff = Fraction(entry["coeff"])
                _add_scaled(
                    polynomial,
                    _word_polynomial(entry["words"], n),
                    coeff,
                )
            result[name] = {
                "schema": {
                    "standard_form": terms,
                    "frappat_form": frappat_form,
                    "parity": parity,
                },
                "polynomial": _clean(polynomial),
                "parity": parity,
            }
    return result


@dataclass
class _Pivot:
    polynomial: Polynomial
    coordinates: dict[int, Fraction]


class _Span:
    """Exact coordinate solver for the span of independent basis realizations."""

    def __init__(self, polynomials: list[Polynomial]):
        self.pivots: dict[Monomial, _Pivot] = {}
        for index, polynomial in enumerate(polynomials):
            reduced = dict(polynomial)
            coordinates = {index: Fraction(1)}
            self._reduce(reduced, coordinates)
            if not reduced:
                raise ValueError(f"Basis realization {index} is linearly dependent")
            pivot = min(reduced)
            scale = reduced[pivot]
            normalized = {
                monomial: coeff / scale for monomial, coeff in reduced.items()
            }
            normalized_coordinates = {
                coordinate: coeff / scale
                for coordinate, coeff in coordinates.items()
                if coeff
            }
            self.pivots[pivot] = _Pivot(normalized, normalized_coordinates)

    def _reduce(
        self,
        polynomial: Polynomial,
        coordinates: dict[int, Fraction],
    ) -> None:
        for pivot in sorted(self.pivots):
            scale = polynomial.get(pivot, Fraction())
            if not scale:
                continue
            basis_pivot = self.pivots[pivot]
            _add_scaled(polynomial, basis_pivot.polynomial, -scale)
            for index, coeff in basis_pivot.coordinates.items():
                coordinates[index] = coordinates.get(index, Fraction()) - (
                    scale * coeff
                )
                if not coordinates[index]:
                    del coordinates[index]

    def coordinates(self, polynomial: Polynomial) -> dict[int, Fraction]:
        reduced = dict(polynomial)
        result: dict[int, Fraction] = {}
        for pivot in sorted(self.pivots):
            scale = reduced.get(pivot, Fraction())
            if not scale:
                continue
            basis_pivot = self.pivots[pivot]
            _add_scaled(reduced, basis_pivot.polynomial, -scale)
            for index, coeff in basis_pivot.coordinates.items():
                result[index] = result.get(index, Fraction()) + scale * coeff
                if not result[index]:
                    del result[index]
        if reduced:
            raise ValueError(
                "Computed bracket is not in the span of the C(n+1) basis: "
                f"{reduced}"
            )
        return result


def _bracket(left: Polynomial, right: Polynomial, parity: int) -> Polynomial:
    result = _multiply(left, right)
    _add_scaled(
        result,
        _multiply(right, left),
        Fraction(1 if parity else -1),
    )
    return _clean(result)


def _build_structure_constants(
    names: list[str], realizations: dict[str, dict]
) -> list[dict[str, str]]:
    span = _Span([realizations[name]["polynomial"] for name in names])
    constants = []
    for left_name in names:
        left = realizations[left_name]
        for right_name in names:
            right = realizations[right_name]
            parity = left["parity"] * right["parity"]
            bracket = _bracket(
                left["polynomial"], right["polynomial"], parity
            )
            for index, coeff in sorted(span.coordinates(bracket).items()):
                constants.append(
                    {
                        "X": left_name,
                        "Y": right_name,
                        "Z": names[index],
                        "coeff": _fraction_string(coeff),
                        "sign_rule": "graded",
                    }
                )
    return constants


def build_schema(n: int, generation_date: str | None = None) -> dict:
    """Build a complete Schema 1 structure object for the given rank."""
    basis = build_basis(n)
    realizations = build_realizations(n, basis)
    even = basis["even"]
    odd = basis["odd"]
    names = odd + even
    structure_constants = _build_structure_constants(names, realizations)

    fermion_labels = ["a_1_p", "a_1_m"]
    boson_labels = [
        f"b_{index}_{sign}"
        for index in range(1, n + 1)
        for sign in ("p", "m")
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
                "total": 2 * n**2 + 5 * n + 1,
                "even": 2 * n**2 + n + 1,
                "odd": 4 * n,
            },
            "dimension_formula": {
                "total": "2n^2 + 5n + 1",
                "even": "2n^2 + n + 1",
                "odd": "4n",
            },
        },
        "oscillator_generators": {
            "fermions": {
                "m": 1,
                "labels": fermion_labels,
                "parity": 1,
                "description": "Standard fermionic pair a_1^+, a_1^-",
            },
            "bosons": {
                "count": 2 * n,
                "n": n,
                "labels": boson_labels,
                "parity": 0,
                "description": "Bosonic oscillators b_i^± for i=1,...,n",
            },
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": (
                    "Canonical anticommutation relations for the fermionic pair"
                ),
                "relations": {
                    "conjugate_pair": "{a_1^-, a_1^+} = 1",
                    "same_type": (
                        "{a_1^+, a_1^+} = {a_1^-, a_1^-} = 0"
                    ),
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
                "boson_fermion": (
                    "[b_i^±, a_1^±] = 0 for all i and fermion signs"
                )
            },
        },
        "central_elements": {
            "kappa": {
                "parity": 1,
                "central": True,
                "nilpotent": True,
                "description": "Odd central symbol for the inhomogeneous extension",
            },
            "K": {
                "parity": 0,
                "central": True,
                "identity": True,
                "description": "Even scalar identity, K=1",
            },
        },
        "basis": basis,
        "parity": {
            **{name: 0 for name in even},
            **{name: 1 for name in odd},
        },
        "generator_realization": {
            "description": "Standard form with PBW ordering",
            "ordering": fermion_labels + boson_labels,
            "realizations": {
                name: realizations[name]["schema"] for name in even + odd
            },
        },
        "structure_constants": structure_constants,
        "metadata": {
            "generated_by": "C_generators.py",
            "generation_date": generation_date or date.today().isoformat(),
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "C(n+1) mathematical definition and oscillator realization",
            ],
        },
    }


def write_schema(n: int, output_dir: Path, generation_date: str | None = None) -> Path:
    schema = build_schema(n, generation_date)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"C_{n}_structure.json"
    output_path.write_text(
        json.dumps(schema, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate C(n+1) Schema 1 structure JSON files."
    )
    parser.add_argument(
        "n",
        nargs="*",
        type=int,
        choices=(1, 2, 3),
        default=None,
        help="bosonic rank(s) to generate; defaults to 1, 2, and 3",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "data",
        help="directory for generated JSON files",
    )
    args = parser.parse_args()
    for n in args.n or (1, 2, 3):
        print(write_schema(n, args.output_dir))


if __name__ == "__main__":
    main()
