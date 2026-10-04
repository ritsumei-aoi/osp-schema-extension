#!/usr/bin/env python3
"""Compute first-order inhomogeneous gamma data for C(n+1)."""

from __future__ import annotations

import argparse
import json
from datetime import date
from fractions import Fraction
from pathlib import Path
from typing import TypeAlias

if __package__:
    from .C_generators import (
        DATA_DIR,
        _basis_realizations,
        _decompose,
        _oscillator_order,
    )
else:
    from C_generators import (
        DATA_DIR,
        _basis_realizations,
        _decompose,
        _oscillator_order,
    )


Word: TypeAlias = tuple[str, ...]
Parameter: TypeAlias = str | None
Term: TypeAlias = tuple[Word, Parameter]
PerturbedPolynomial: TypeAlias = dict[Term, Fraction]


def _parameter_label(fermion: str, boson: str) -> str:
    return f"gb_{fermion}_{boson}"


def _normal_order_word(
    word: Word,
    parameter: Parameter,
    order: dict[str, int],
) -> PerturbedPolynomial:
    for index in range(len(word) - 1):
        left, right = word[index : index + 2]
        if left in ("a_1_p", "a_1_m") and left == right:
            return {}
        if order[left] > order[right]:
            swapped = word[:index] + (right, left) + word[index + 2 :]
            if (left, right) == ("a_1_m", "a_1_p"):
                reduced = _normal_order_word(swapped, parameter, order)
                reduced = {term: -coefficient for term, coefficient in reduced.items()}
                contracted = _normal_order_word(
                    word[:index] + word[index + 2 :], parameter, order
                )
                _add_scaled(reduced, contracted, Fraction(1))
                return reduced
            if left.startswith("b_") and left.endswith("_m") and right.startswith("b_") and right.endswith("_p"):
                reduced = _normal_order_word(swapped, parameter, order)
                if left.split("_")[1] == right.split("_")[1]:
                    contracted = _normal_order_word(
                        word[:index] + word[index + 2 :], parameter, order
                    )
                    _add_scaled(reduced, contracted, Fraction(1))
                return reduced
            if left.startswith("b_") and right in ("a_1_p", "a_1_m"):
                reduced = _normal_order_word(swapped, parameter, order)
                if parameter is None:
                    contraction = _normal_order_word(
                        word[:index] + word[index + 2 :],
                        _parameter_label(right, left),
                        order,
                    )
                    prefix_parity = sum(
                        token in ("a_1_p", "a_1_m") for token in word[:index]
                    ) % 2
                    _add_scaled(
                        reduced,
                        contraction,
                        Fraction(1) if prefix_parity else Fraction(-1),
                    )
                return reduced
            return _normal_order_word(swapped, parameter, order)
    return {(word, parameter): Fraction(1)}


def _add_scaled(
    target: PerturbedPolynomial,
    source: PerturbedPolynomial,
    scale: Fraction,
) -> None:
    if not scale:
        return
    for term, coefficient in source.items():
        target[term] = target.get(term, Fraction(0)) + scale * coefficient
        if not target[term]:
            del target[term]


def _multiply(
    left: PerturbedPolynomial,
    right: PerturbedPolynomial,
    order: dict[str, int],
) -> PerturbedPolynomial:
    result: PerturbedPolynomial = {}
    for (left_word, left_parameter), left_coefficient in left.items():
        for (right_word, right_parameter), right_coefficient in right.items():
            if left_parameter is not None and right_parameter is not None:
                continue
            parameter = left_parameter or right_parameter
            normal = _normal_order_word(left_word + right_word, parameter, order)
            _add_scaled(result, normal, left_coefficient * right_coefficient)
    return result


def _perturb(polynomial: dict[Word, Fraction]) -> PerturbedPolynomial:
    return {(word, None): coefficient for word, coefficient in polynomial.items()}


def _bracket(
    left: PerturbedPolynomial,
    right: PerturbedPolynomial,
    left_parity: int,
    right_parity: int,
    order: dict[str, int],
) -> PerturbedPolynomial:
    result = _multiply(left, right, order)
    reverse = _multiply(right, left, order)
    _add_scaled(
        result,
        reverse,
        Fraction(-1) if not (left_parity and right_parity) else Fraction(1),
    )
    return result


def build_gamma_schema(rank: int, structure_schema: dict[str, object]) -> dict[str, object]:
    if rank < 1:
        raise ValueError("The bosonic rank n must be at least 1")
    if structure_schema["algebra"]["family"] != "C" or structure_schema["algebra"]["n"] != rank:
        raise ValueError(f"Structure schema does not match C rank {rank}")
    basis, realizations, parity = _basis_realizations(rank)
    if structure_schema["generator_realization"]["realizations"].keys() != realizations.keys():
        raise ValueError(f"Structure basis ordering does not match rank {rank}")
    if structure_schema["parity"] != parity:
        raise ValueError(f"Structure parity does not match rank {rank}")

    order = _oscillator_order(rank)
    perturbed = {label: _perturb(realizations[label]) for label in basis}
    gamma_basis = [*basis, "K"]
    gamma_realizations = {**realizations, "K": {(): Fraction(1)}}
    gamma_entries: list[dict[str, str]] = []
    for left_index, left_label in enumerate(basis):
        for right_label in basis[left_index:]:
            bracket = _bracket(
                perturbed[left_label],
                perturbed[right_label],
                parity[left_label],
                parity[right_label],
                order,
            )
            by_parameter: dict[str, dict[Word, Fraction]] = {}
            for (word, parameter), coefficient in bracket.items():
                if parameter is None:
                    continue
                polynomial = by_parameter.setdefault(parameter, {})
                polynomial[word] = polynomial.get(word, Fraction(0)) + coefficient
                if not polynomial[word]:
                    del polynomial[word]
            for parameter, polynomial in by_parameter.items():
                decomposition = _decompose(
                    polynomial, gamma_basis, gamma_realizations
                )
                gamma_entries.extend(
                    {
                        "X": left_label,
                        "Y": right_label,
                        "Z": output_label,
                        "gb": parameter,
                        "coeff": str(coefficient),
                        "sign_rule": "graded",
                    }
                    for output_label, coefficient in decomposition.items()
                )

    gb_matrix = {
        fermion: {
            boson: _parameter_label(fermion, boson)
            for k in range(1, rank + 1)
            for boson in (f"b_{k}_p", f"b_{k}_m")
        }
        for fermion in ("a_1_p", "a_1_m")
    }
    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": rank,
            "cartan_type": f"C({rank + 1})",
            "dimension": structure_schema["algebra"]["dimension"],
        },
        "source_schema": f"C_{rank}_structure.json",
        "gb_matrix": {
            "shape": [2, 2 * rank],
            "row_labels": ["a_1_p", "a_1_m"],
            "column_labels": [
                label
                for k in range(1, rank + 1)
                for label in (f"b_{k}_p", f"b_{k}_m")
            ],
            "entries": gb_matrix,
            "parameter_parity": 0,
        },
        "inhomogeneous_deformation": {
            "description": "First-order mixed fermion-boson deformation",
            "relations": [
                {
                    "X": boson,
                    "Y": fermion,
                    "relation": f"[{boson}, {fermion}] = -{parameter} * κ",
                    "gb": parameter,
                }
                for fermion, columns in gb_matrix.items()
                for boson, parameter in columns.items()
            ],
            "kappa": {"label": "κ", "parity": 1, "central": True, "nilpotent": True},
            "truncation": "Retain terms linear in gb*κ; terms containing κ^2 vanish",
        },
        "gamma_structure": gamma_entries,
        "metadata": {
            "generated_by": "src/C_gamma.py",
            "generation_date": date.today().isoformat(),
            "references": [
                "docs/math/C_inhomogeneous_definition.md",
                "docs/json_schema_specification.md",
            ],
        },
    }


def write_gamma(rank: int, data_dir: Path = DATA_DIR) -> Path:
    structure_path = data_dir / f"C_{rank}_structure.json"
    with structure_path.open(encoding="utf-8") as stream:
        structure_schema = json.load(stream)
    gamma = build_gamma_schema(rank, structure_schema)
    output_path = data_dir / f"C_{rank}_gamma.json"
    output_path.write_text(
        json.dumps(gamma, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ranks", type=int, nargs="+", default=[1, 2, 3])
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    arguments = parser.parse_args()
    for rank in arguments.ranks:
        print(write_gamma(rank, arguments.data_dir))


if __name__ == "__main__":
    main()
