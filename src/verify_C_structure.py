#!/usr/bin/env python3
"""Verify graded anti-symmetry and the Super Jacobi identity in C structure files."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Mapping

Bracket = dict[tuple[str, str], dict[str, Fraction]]


@dataclass(frozen=True)
class VerificationResult:
    path: Path
    rank: int
    basis_size: int
    term_count: int
    pair_count: int
    antisymmetry_failures: tuple[str, ...]
    triple_count: int
    jacobi_failures: tuple[str, ...]


def _load_structure(
    path: Path,
) -> tuple[int, tuple[str, ...], dict[str, int], Bracket, int]:
    data = json.loads(path.read_text(encoding="utf-8"))
    try:
        rank = data["algebra"]["n"]
        even = data["basis"]["even"]
        odd = data["basis"]["odd"]
        parity = data["parity"]
        records = data["structure_constants"]
    except (KeyError, TypeError) as exc:
        raise ValueError(f"{path}: missing or invalid Schema 1 fields") from exc

    if not isinstance(rank, int) or rank < 1:
        raise ValueError(f"{path}: algebra.n must be a positive integer")
    if (
        not isinstance(even, list)
        or not isinstance(odd, list)
        or not isinstance(parity, dict)
    ):
        raise ValueError(f"{path}: basis or parity has an invalid type")
    basis = tuple(even + odd)
    if any(not isinstance(label, str) for label in basis):
        raise ValueError(f"{path}: basis labels must be strings")
    if len(set(basis)) != len(basis):
        raise ValueError(f"{path}: basis contains duplicate generator labels")
    if set(parity) != set(basis):
        raise ValueError(f"{path}: parity labels do not match the basis")
    if any(parity[label] not in (0, 1) for label in basis):
        raise ValueError(f"{path}: parity values must be 0 or 1")
    if any(parity[label] != 0 for label in even) or any(
        parity[label] != 1 for label in odd
    ):
        raise ValueError(f"{path}: basis parity disagrees with the parity map")
    if not isinstance(records, list):
        raise ValueError(f"{path}: structure_constants must be a list")

    bracket: Bracket = {}
    seen: set[tuple[str, str, str]] = set()
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError(f"{path}: structure_constants[{index}] must be an object")
        try:
            left, right, output = record["X"], record["Y"], record["Z"]
            sign_rule = record["sign_rule"]
            coefficient_text = record["coeff"]
        except (KeyError, TypeError) as exc:
            raise ValueError(f"{path}: invalid structure_constants[{index}]") from exc
        if not all(isinstance(label, str) for label in (left, right, output)):
            raise ValueError(f"{path}: invalid generator label in structure_constants[{index}]")
        if not isinstance(coefficient_text, str):
            raise ValueError(f"{path}: coefficient must be a string in structure_constants[{index}]")
        try:
            coefficient = Fraction(coefficient_text)
        except (ValueError, ZeroDivisionError) as exc:
            raise ValueError(f"{path}: invalid coefficient in structure_constants[{index}]") from exc
        if left not in parity or right not in parity or output not in parity:
            raise ValueError(f"{path}: unknown generator in structure_constants[{index}]")
        if sign_rule != "graded":
            raise ValueError(f"{path}: unsupported sign_rule in structure_constants[{index}]")
        if not coefficient:
            raise ValueError(f"{path}: zero coefficient in structure_constants[{index}]")
        key = (left, right, output)
        if key in seen:
            raise ValueError(f"{path}: duplicate structure constant {key}")
        seen.add(key)
        bracket.setdefault((left, right), {})[output] = coefficient

    return rank, basis, parity, bracket, len(records)


def _nested_bracket(
    bracket: Bracket, left: str, inner: Mapping[str, Fraction]
) -> dict[str, Fraction]:
    result: defaultdict[str, Fraction] = defaultdict(Fraction)
    for middle, inner_coefficient in inner.items():
        for output, outer_coefficient in bracket.get((left, middle), {}).items():
            result[output] += inner_coefficient * outer_coefficient
    return {label: coefficient for label, coefficient in result.items() if coefficient}


def verify_structure(path: Path) -> VerificationResult:
    rank, basis, parity, bracket, term_count = _load_structure(path)
    antisymmetry_failures: list[str] = []
    for left, right in product(basis, repeat=2):
        sign = -1 if parity[left] * parity[right] == 0 else 1
        expected_reverse = {
            output: sign * coefficient
            for output, coefficient in bracket.get((left, right), {}).items()
        }
        actual_reverse = bracket.get((right, left), {})
        if expected_reverse != actual_reverse:
            antisymmetry_failures.append(
                f"[{left},{right}] vs [{right},{left}]: "
                f"expected reverse {expected_reverse}, found {actual_reverse}"
            )

    jacobi_failures: list[str] = []
    for x, y, z in product(basis, repeat=3):
        terms = (
            (-1 if parity[x] * parity[z] else 1, x, y, z),
            (-1 if parity[y] * parity[x] else 1, y, z, x),
            (-1 if parity[z] * parity[y] else 1, z, x, y),
        )
        total: defaultdict[str, Fraction] = defaultdict(Fraction)
        for sign, outer, inner_left, inner_right in terms:
            inner = bracket.get((inner_left, inner_right), {})
            for output, coefficient in _nested_bracket(bracket, outer, inner).items():
                total[output] += sign * coefficient
        nonzero = {
            label: coefficient
            for label, coefficient in total.items()
            if coefficient
        }
        if nonzero:
            jacobi_failures.append(f"({x}, {y}, {z}): {nonzero}")

    basis_size = len(basis)
    return VerificationResult(
        path=path,
        rank=rank,
        basis_size=basis_size,
        term_count=term_count,
        pair_count=basis_size**2,
        antisymmetry_failures=tuple(antisymmetry_failures),
        triple_count=basis_size**3,
        jacobi_failures=tuple(jacobi_failures),
    )


def _print_failures(title: str, failures: tuple[str, ...], limit: int = 10) -> None:
    for failure in failures[:limit]:
        print(f"  {title}: {failure}")
    if len(failures) > limit:
        print(f"  ... and {len(failures) - limit} more {title.lower()} failure(s)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ranks",
        type=int,
        nargs="+",
        default=[1, 2, 3],
        help="Bosonic ranks to verify (default: 1 2 3)",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data",
        help="Directory containing C_<n>_structure.json files",
    )
    arguments = parser.parse_args()

    overall_pass = True
    for rank in arguments.ranks:
        path = arguments.data_dir / f"C_{rank}_structure.json"
        if not path.is_file():
            raise FileNotFoundError(f"Structure file does not exist: {path}")
        result = verify_structure(path)
        anti_pass = not result.antisymmetry_failures
        jacobi_pass = not result.jacobi_failures
        overall_pass &= anti_pass and jacobi_pass
        print(
            f"C({rank + 1}): basis={result.basis_size}, "
            f"nonzero_terms={result.term_count}; "
            f"graded anti-symmetry "
            f"{'PASS' if anti_pass else 'FAIL'} "
            f"({result.pair_count} ordered pairs); Super Jacobi "
            f"{'PASS' if jacobi_pass else 'FAIL'} "
            f"({result.triple_count} ordered triples)"
        )
        _print_failures("ANTI-SYMMETRY", result.antisymmetry_failures)
        _print_failures("JACOBI", result.jacobi_failures)

    print(f"Overall: {'PASS' if overall_pass else 'FAIL'}")
    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
