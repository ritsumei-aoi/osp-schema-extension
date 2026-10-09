#!/usr/bin/env python3
"""Verify graded anti-symmetry and Super Jacobi for generated C(n+1) data."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import TypeAlias

BracketMap: TypeAlias = dict[tuple[str, str], dict[str, Fraction]]
DEFAULT_DATA_DIR = Path(__file__).resolve().parents[1] / "data"


class VerificationError(Exception):
    """Raised when a structure file or one of its identities is invalid."""


@dataclass(frozen=True)
class VerificationResult:
    rank: int
    basis_size: int
    pair_checks: int
    triple_checks: int
    structure_constant_records: int


def _add_scaled(
    target: dict[str, Fraction],
    source: dict[str, Fraction],
    scale: Fraction,
) -> None:
    for label, coefficient in source.items():
        value = target.get(label, Fraction(0)) + scale * coefficient
        if value:
            target[label] = value
        else:
            target.pop(label, None)


def _parse_coefficient(value: object, context: str) -> Fraction:
    if not isinstance(value, str):
        raise VerificationError(f"{context}: coefficient must be a rational string.")
    try:
        coefficient = Fraction(value)
    except (TypeError, ValueError, ZeroDivisionError) as error:
        raise VerificationError(f"{context}: invalid rational coefficient {value!r}.") from error
    if not coefficient:
        raise VerificationError(f"{context}: structure-constant coefficient is zero.")
    return coefficient


def _load_brackets(
    data: dict[str, object],
) -> tuple[list[str], dict[str, int], BracketMap, int]:
    try:
        basis = data["basis"]
        even = basis["even"]
        odd = basis["odd"]
        parity = data["parity"]
        records = data["structure_constants"]
    except (KeyError, TypeError) as error:
        raise VerificationError("Missing basis, parity, or structure_constants data.") from error

    if (
        not isinstance(even, list)
        or not isinstance(odd, list)
        or not all(isinstance(label, str) for label in even + odd)
    ):
        raise VerificationError("basis.even and basis.odd must be lists of labels.")
    labels = odd + even
    if len(labels) != len(set(labels)):
        raise VerificationError("Basis labels must be unique across parity blocks.")
    if not isinstance(parity, dict) or set(parity) != set(labels):
        raise VerificationError("Parity map must contain exactly the basis labels.")
    if any(type(value) is not int or value not in (0, 1) for value in parity.values()):
        raise VerificationError("Every basis parity must be the integer 0 or 1.")
    if any(parity[label] != 1 for label in odd) or any(parity[label] != 0 for label in even):
        raise VerificationError("Basis blocks do not agree with the parity map.")
    if not isinstance(records, list):
        raise VerificationError("structure_constants must be a list.")

    brackets: BracketMap = {}
    seen: set[tuple[str, str, str]] = set()
    required_record_keys = {"X", "Y", "Z", "coeff", "sign_rule"}
    for index, record in enumerate(records):
        context = f"structure_constants[{index}]"
        if not isinstance(record, dict) or set(record) != required_record_keys:
            raise VerificationError(f"{context}: expected X, Y, Z, coeff, and sign_rule fields.")
        x, y, z = record["X"], record["Y"], record["Z"]
        if not all(isinstance(label, str) and label in parity for label in (x, y, z)):
            raise VerificationError(f"{context}: bracket labels must refer to basis elements.")
        if record["sign_rule"] != "graded":
            raise VerificationError(f"{context}: sign_rule must be 'graded'.")
        key = (x, y, z)
        if key in seen:
            raise VerificationError(f"{context}: duplicate bracket record {key}.")
        seen.add(key)
        coefficient = _parse_coefficient(record["coeff"], context)
        brackets.setdefault((x, y), {})[z] = coefficient
    return labels, parity, brackets, len(records)


def _linear_bracket(
    left: str,
    right_combination: dict[str, Fraction],
    brackets: BracketMap,
) -> dict[str, Fraction]:
    result: dict[str, Fraction] = {}
    for right, coefficient in right_combination.items():
        _add_scaled(result, brackets.get((left, right), {}), coefficient)
    return result


def _verify_graded_antisymmetry(
    labels: list[str],
    parity: dict[str, int],
    brackets: BracketMap,
) -> int:
    checks = 0
    for x in labels:
        for y in labels:
            sign = -1 if parity[x] * parity[y] else 1
            expected = {
                z: -sign * coefficient
                for z, coefficient in brackets.get((x, y), {}).items()
            }
            if brackets.get((y, x), {}) != expected:
                raise VerificationError(
                    f"Graded anti-symmetry failed for pair ({x}, {y}): "
                    f"bracket is {brackets.get((x, y), {})}, "
                    f"expected reverse bracket {expected}."
                )
            checks += 1
    return checks


def _jacobi_sum(
    x: str,
    y: str,
    z: str,
    parity: dict[str, int],
    brackets: BracketMap,
) -> dict[str, Fraction]:
    terms = (
        (-1 if parity[x] * parity[z] else 1, x, brackets.get((y, z), {})),
        (-1 if parity[y] * parity[x] else 1, y, brackets.get((z, x), {})),
        (-1 if parity[z] * parity[y] else 1, z, brackets.get((x, y), {})),
    )
    result: dict[str, Fraction] = {}
    for sign, left, inner_bracket in terms:
        _add_scaled(result, _linear_bracket(left, inner_bracket, brackets), sign)
    return result


def _verify_super_jacobi(
    labels: list[str],
    parity: dict[str, int],
    brackets: BracketMap,
) -> int:
    checks = 0
    for x in labels:
        for y in labels:
            for z in labels:
                residual = _jacobi_sum(x, y, z, parity, brackets)
                if residual:
                    raise VerificationError(
                        f"Super Jacobi failed for ({x}, {y}, {z}): {residual}."
                    )
                checks += 1
    return checks


def verify_data(data: dict[str, object], rank: int) -> VerificationResult:
    """Validate one loaded structure object and all pair/triple identities."""
    try:
        algebra = data["algebra"]
        actual_rank = algebra["n"]
        even_dimension = algebra["dimension"]["even"]
        odd_dimension = algebra["dimension"]["odd"]
        total_dimension = algebra["dimension"]["total"]
    except (KeyError, TypeError) as error:
        raise VerificationError("Missing algebra rank or dimension fields.") from error

    expected_even = 2 * rank * rank + rank + 1
    expected_odd = 4 * rank
    if actual_rank != rank:
        raise VerificationError(f"Expected algebra rank {rank}, found {actual_rank}.")
    if (even_dimension, odd_dimension, total_dimension) != (
        expected_even,
        expected_odd,
        expected_even + expected_odd,
    ):
        raise VerificationError("Algebra dimensions do not match the C(n+1) formulas.")

    labels, parity, brackets, record_count = _load_brackets(data)
    if len(labels) != total_dimension:
        raise VerificationError(
            f"Basis has {len(labels)} labels but algebra dimension is {total_dimension}."
        )
    pair_checks = _verify_graded_antisymmetry(labels, parity, brackets)
    triple_checks = _verify_super_jacobi(labels, parity, brackets)
    return VerificationResult(
        rank=rank,
        basis_size=len(labels),
        pair_checks=pair_checks,
        triple_checks=triple_checks,
        structure_constant_records=record_count,
    )


def verify_file(path: Path, rank: int) -> VerificationResult:
    """Load and verify a single rank-specific structure JSON file."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise VerificationError(f"Could not load {path}: {error}") from error
    if not isinstance(data, dict):
        raise VerificationError(f"{path}: top-level JSON value must be an object.")
    return verify_data(data, rank)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DEFAULT_DATA_DIR,
        help="Directory containing C_{n}_structure.json files.",
    )
    parser.add_argument(
        "--ranks",
        type=int,
        nargs="+",
        default=[1, 2, 3],
        help="Bosonic ranks to verify (default: 1 2 3).",
    )
    args = parser.parse_args(argv)

    failed = False
    for rank in args.ranks:
        path = args.data_dir / f"C_{rank}_structure.json"
        try:
            result = verify_file(path, rank)
        except VerificationError as error:
            print(f"C_{rank}: FAIL — {error}")
            failed = True
            continue
        print(
            f"C_{rank}: PASS; basis={result.basis_size}, "
            f"ordered pairs={result.pair_checks}, "
            f"ordered triples={result.triple_checks}, "
            f"structure-constant records={result.structure_constant_records}"
        )
    if failed:
        print("Verification failed for one or more ranks.", file=sys.stderr)
        return 1
    print("All requested C(n+1) structure files passed verification.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
