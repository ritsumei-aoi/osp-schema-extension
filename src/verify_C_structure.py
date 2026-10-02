"""Verify graded anti-symmetry and Super Jacobi for generated C(n+1) JSON."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

DEFAULT_FILES = (
    Path("data/C_1_structure.json"),
    Path("data/C_2_structure.json"),
    Path("data/C_3_structure.json"),
)


class VerificationError(ValueError):
    """An invalid schema record or failed algebra identity."""


@dataclass(frozen=True)
class VerificationReport:
    path: Path
    basis_size: int
    pair_checks: int
    triple_checks: int
    constant_entries: int


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise VerificationError(f"Duplicate JSON object key: {key}")
        result[key] = value
    return result


def _load_schema(path: Path) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as source:
            schema = json.load(source, object_pairs_hook=_reject_duplicate_keys)
    except OSError as error:
        raise VerificationError(f"Cannot read {path}: {error}") from error
    except json.JSONDecodeError as error:
        raise VerificationError(f"Invalid JSON in {path}: {error}") from error
    if not isinstance(schema, dict):
        raise VerificationError(f"{path}: top-level JSON value must be an object")
    return schema


def _validate_basis(schema: dict[str, Any], path: Path) -> tuple[list[str], dict[str, int]]:
    try:
        algebra = schema["algebra"]
        n = algebra["n"]
        dimension = algebra["dimension"]
        even = schema["basis"]["even"]
        odd = schema["basis"]["odd"]
        parity = schema["parity"]
    except (KeyError, TypeError) as error:
        raise VerificationError(f"{path}: missing or malformed basis fields: {error}") from error

    if schema.get("schema_version") != "5.0":
        raise VerificationError(f"{path}: expected schema_version '5.0'")
    if algebra.get("family") != "C" or algebra.get("m") != 1:
        raise VerificationError(f"{path}: expected C family with m=1")
    if isinstance(n, bool) or not isinstance(n, int) or n < 1:
        raise VerificationError(f"{path}: algebra.n must be a positive integer")
    if not isinstance(even, list) or not isinstance(odd, list):
        raise VerificationError(f"{path}: basis.even and basis.odd must be arrays")
    if not all(isinstance(label, str) for label in even + odd):
        raise VerificationError(f"{path}: all basis labels must be strings")

    labels = even + odd
    if len(labels) != len(set(labels)):
        raise VerificationError(f"{path}: basis contains duplicate labels")
    expected_even = 2 * n * n + n + 1
    expected_odd = 4 * n
    expected_total = expected_even + expected_odd
    if len(even) != expected_even or len(odd) != expected_odd:
        raise VerificationError(
            f"{path}: basis sizes are {len(even)}|{len(odd)}, expected "
            f"{expected_even}|{expected_odd}"
        )
    if dimension != {
        "even": expected_even,
        "odd": expected_odd,
        "total": expected_total,
    }:
        raise VerificationError(f"{path}: algebra dimensions do not match its basis")
    if not isinstance(parity, dict) or set(parity) != set(labels):
        raise VerificationError(f"{path}: parity keys must match basis labels exactly")
    if any(type(parity[label]) is not int or parity[label] != 0 for label in even):
        raise VerificationError(f"{path}: every even basis label must have parity 0")
    if any(type(parity[label]) is not int or parity[label] != 1 for label in odd):
        raise VerificationError(f"{path}: every odd basis label must have parity 1")

    return odd + even, parity


def _load_brackets(
    schema: dict[str, Any], labels: list[str], path: Path
) -> dict[tuple[str, str], dict[str, Fraction]]:
    records = schema.get("structure_constants")
    if not isinstance(records, list):
        raise VerificationError(f"{path}: structure_constants must be an array")

    label_set = set(labels)
    brackets: dict[tuple[str, str], dict[str, Fraction]] = defaultdict(dict)
    seen: set[tuple[str, str, str]] = set()
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise VerificationError(f"{path}: structure_constants[{index}] must be an object")
        required = {"X", "Y", "Z", "coeff", "sign_rule"}
        if set(record) != required:
            raise VerificationError(
                f"{path}: structure_constants[{index}] must have exactly {sorted(required)}"
            )
        x, y, z = record["X"], record["Y"], record["Z"]
        if any(not isinstance(label, str) or label not in label_set for label in (x, y, z)):
            raise VerificationError(
                f"{path}: structure_constants[{index}] references an unknown basis label"
            )
        if record["sign_rule"] != "graded":
            raise VerificationError(
                f"{path}: structure_constants[{index}] has invalid sign_rule"
            )
        if not isinstance(record["coeff"], str):
            raise VerificationError(
                f"{path}: structure_constants[{index}].coeff must be a rational string"
            )
        try:
            coefficient = Fraction(record["coeff"])
        except (ValueError, ZeroDivisionError) as error:
            raise VerificationError(
                f"{path}: invalid rational coefficient at structure_constants[{index}]"
            ) from error
        if coefficient == 0:
            raise VerificationError(
                f"{path}: structure_constants[{index}] stores a zero coefficient"
            )
        triplet = (x, y, z)
        if triplet in seen:
            raise VerificationError(f"{path}: duplicate structure-constant entry {triplet}")
        seen.add(triplet)
        brackets[(x, y)][z] = coefficient
    return brackets


def _add_scaled(
    destination: dict[str, Fraction],
    source: dict[str, Fraction],
    scale: Fraction,
) -> None:
    for label, coefficient in source.items():
        value = destination.get(label, Fraction(0)) + scale * coefficient
        if value:
            destination[label] = value
        else:
            destination.pop(label, None)


def _nested_bracket(
    brackets: dict[tuple[str, str], dict[str, Fraction]],
    left: str,
    right_bracket: dict[str, Fraction],
) -> dict[str, Fraction]:
    result: dict[str, Fraction] = {}
    for right_generator, coefficient in right_bracket.items():
        _add_scaled(result, brackets.get((left, right_generator), {}), coefficient)
    return result


def _format_residual(residual: dict[str, Fraction]) -> str:
    return "{" + ", ".join(
        f"{label}: {coefficient}" for label, coefficient in sorted(residual.items())
    ) + "}"


def verify_file(path: str | Path) -> VerificationReport:
    """Verify all ordered pairs and triples in one generated schema file."""
    path = Path(path)
    schema = _load_schema(path)
    labels, parity = _validate_basis(schema, path)
    brackets = _load_brackets(schema, labels, path)

    pair_checks = 0
    for x in labels:
        for y in labels:
            pair_checks += 1
            sign = -1 if parity[x] * parity[y] else 1
            expected = {
                z: -sign * coefficient
                for z, coefficient in brackets.get((y, x), {}).items()
            }
            actual = brackets.get((x, y), {})
            if actual != expected:
                raise VerificationError(
                    f"{path}: graded anti-symmetry failed for ({x}, {y}); "
                    f"actual={_format_residual(actual)}, "
                    f"expected={_format_residual(expected)}"
                )

    triple_checks = 0
    for x in labels:
        for y in labels:
            for z in labels:
                triple_checks += 1
                first = _nested_bracket(
                    brackets, x, brackets.get((y, z), {})
                )
                second = _nested_bracket(
                    brackets, y, brackets.get((z, x), {})
                )
                third = _nested_bracket(
                    brackets, z, brackets.get((x, y), {})
                )
                residual: dict[str, Fraction] = {}
                _add_scaled(
                    residual,
                    first,
                    Fraction(-1 if parity[x] * parity[z] else 1),
                )
                _add_scaled(
                    residual,
                    second,
                    Fraction(-1 if parity[y] * parity[x] else 1),
                )
                _add_scaled(
                    residual,
                    third,
                    Fraction(-1 if parity[z] * parity[y] else 1),
                )
                if residual:
                    raise VerificationError(
                        f"{path}: Super Jacobi failed for ({x}, {y}, {z}); "
                        f"residual={_format_residual(residual)} "
                        f"after {triple_checks} triple checks"
                    )

    return VerificationReport(
        path=path,
        basis_size=len(labels),
        pair_checks=pair_checks,
        triple_checks=triple_checks,
        constant_entries=sum(len(values) for values in brackets.values()),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "files",
        nargs="*",
        type=Path,
        default=DEFAULT_FILES,
        help="Schema files to verify (default: the n=1,2,3 files in data/)",
    )
    args = parser.parse_args()

    failed = False
    total_pairs = 0
    total_triples = 0
    for path in args.files:
        try:
            report = verify_file(path)
        except VerificationError as error:
            failed = True
            print(f"FAIL {path}: {error}", file=sys.stderr)
            continue
        total_pairs += report.pair_checks
        total_triples += report.triple_checks
        print(
            f"PASS {report.path}: basis={report.basis_size}, "
            f"constants={report.constant_entries}, "
            f"anti-symmetry pairs={report.pair_checks}, "
            f"Super Jacobi triples={report.triple_checks}"
        )

    if failed:
        print("Verification failed.", file=sys.stderr)
        return 1
    print(
        f"PASS all files: anti-symmetry pairs={total_pairs}, "
        f"Super Jacobi triples={total_triples}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
