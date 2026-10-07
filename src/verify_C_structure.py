#!/usr/bin/env python3
"""Verify graded anti-symmetry and the Super Jacobi identity in C schemas."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Mapping

Vector = dict[str, Fraction]
BracketTable = dict[tuple[str, str], Vector]
MAX_FAILURE_SAMPLES = 10


@dataclass
class VerificationReport:
    path: Path
    algebra: str
    generator_count: int
    constant_count: int
    parity_failures: int = 0
    antisymmetry_checks: int = 0
    antisymmetry_failures: int = 0
    jacobi_checks: int = 0
    jacobi_failures: int = 0
    samples: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not (
            self.parity_failures
            or self.antisymmetry_failures
            or self.jacobi_failures
        )


def _add_scaled(target: Vector, source: Mapping[str, Fraction], scale: Fraction) -> None:
    for name, coefficient in source.items():
        value = target.get(name, Fraction()) + scale * coefficient
        if value:
            target[name] = value
        else:
            target.pop(name, None)


def _format_vector(vector: Mapping[str, Fraction]) -> str:
    if not vector:
        return "{}"
    terms = ", ".join(
        f"{name}: {coefficient}"
        for name, coefficient in sorted(vector.items())
    )
    return "{" + terms + "}"


def _bracket_vectors(
    left: Mapping[str, Fraction],
    right: Mapping[str, Fraction],
    brackets: BracketTable,
) -> Vector:
    result: Vector = {}
    for x, left_coefficient in left.items():
        for y, right_coefficient in right.items():
            for z, coefficient in brackets.get((x, y), {}).items():
                result[z] = result.get(z, Fraction()) + (
                    left_coefficient * right_coefficient * coefficient
                )
    return {name: coefficient for name, coefficient in result.items() if coefficient}


def _validate_schema(data: object, path: Path) -> tuple[list[str], dict[str, int], list[dict]]:
    if not isinstance(data, dict):
        raise ValueError("top-level JSON value must be an object")
    basis = data.get("basis")
    parity = data.get("parity")
    constants = data.get("structure_constants")
    algebra = data.get("algebra")
    if not isinstance(basis, dict) or not isinstance(parity, dict):
        raise ValueError("schema must contain basis and parity objects")
    if not isinstance(constants, list):
        raise ValueError("schema must contain a structure_constants list")
    if not isinstance(algebra, dict) or not isinstance(algebra.get("cartan_type"), str):
        raise ValueError("schema must contain algebra.cartan_type")

    even = basis.get("even")
    odd = basis.get("odd")
    if not isinstance(even, list) or not isinstance(odd, list):
        raise ValueError("basis.even and basis.odd must be lists")
    if not all(isinstance(name, str) for name in even + odd):
        raise ValueError("basis generator labels must all be strings")
    names = odd + even
    if len(set(names)) != len(names):
        raise ValueError("basis contains duplicate generator labels")
    if set(parity) != set(names):
        raise ValueError("parity keys must match the generator basis exactly")
    if any(type(parity[name]) is not int or parity[name] not in (0, 1) for name in names):
        raise ValueError("each generator parity must be integer 0 or 1")

    for index, entry in enumerate(constants):
        if not isinstance(entry, dict):
            raise ValueError(f"structure_constants[{index}] must be an object")
        if not all(key in entry for key in ("X", "Y", "Z", "coeff")):
            raise ValueError(
                f"structure_constants[{index}] must contain X, Y, Z, and coeff"
            )
        if any(entry[key] not in parity for key in ("X", "Y", "Z")):
            raise ValueError(
                f"structure_constants[{index}] refers to an unknown generator"
            )
        if not isinstance(entry["coeff"], str):
            raise ValueError(
                f"structure_constants[{index}].coeff must be a rational string"
            )
        try:
            Fraction(entry["coeff"])
        except (ValueError, ZeroDivisionError) as error:
            raise ValueError(
                f"structure_constants[{index}].coeff is not a valid rational: "
                f"{entry['coeff']!r}"
            ) from error
    return names, parity, constants


def verify_schema(path: Path) -> VerificationReport:
    with path.open(encoding="utf-8") as source:
        data = json.load(source)
    names, parity, constants = _validate_schema(data, path)

    brackets: BracketTable = {}
    report = VerificationReport(
        path=path,
        algebra=data["algebra"]["cartan_type"],
        generator_count=len(names),
        constant_count=len(constants),
    )
    for index, entry in enumerate(constants):
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        coefficient = Fraction(entry["coeff"])
        vector = brackets.setdefault((x, y), {})
        vector[z] = vector.get(z, Fraction()) + coefficient
        if not vector[z]:
            del vector[z]
        if parity[z] != (parity[x] + parity[y]) % 2:
            report.parity_failures += 1
            if len(report.samples) < MAX_FAILURE_SAMPLES:
                report.samples.append(
                    f"parity: constant #{index + 1} [{x}, {y}] -> {z} "
                    f"has parity {parity[z]}, expected "
                    f"{(parity[x] + parity[y]) % 2}"
                )

    for x, y in product(names, repeat=2):
        report.antisymmetry_checks += 1
        left = brackets.get((x, y), {})
        sign = -1 if parity[x] * parity[y] == 0 else 1
        expected = {
            z: sign * coefficient
            for z, coefficient in brackets.get((y, x), {}).items()
        }
        expected = {z: c for z, c in expected.items() if c}
        if left != expected:
            report.antisymmetry_failures += 1
            if len(report.samples) < MAX_FAILURE_SAMPLES:
                report.samples.append(
                    f"anti-symmetry: [{x}, {y}]={_format_vector(left)}, "
                    f"expected {_format_vector(expected)}"
                )

    unit = Fraction(1)
    for x, y, z in product(names, repeat=3):
        report.jacobi_checks += 1
        result: Vector = {}
        _add_scaled(
            result,
            _bracket_vectors({x: unit}, brackets.get((y, z), {}), brackets),
            Fraction(-1 if parity[x] * parity[z] else 1),
        )
        _add_scaled(
            result,
            _bracket_vectors({y: unit}, brackets.get((z, x), {}), brackets),
            Fraction(-1 if parity[y] * parity[x] else 1),
        )
        _add_scaled(
            result,
            _bracket_vectors({z: unit}, brackets.get((x, y), {}), brackets),
            Fraction(-1 if parity[z] * parity[y] else 1),
        )
        if result:
            report.jacobi_failures += 1
            if len(report.samples) < MAX_FAILURE_SAMPLES:
                report.samples.append(
                    f"Jacobi: ({x}, {y}, {z}) has residual "
                    f"{_format_vector(result)}"
                )
    return report


def _print_report(report: VerificationReport) -> None:
    status = "PASS" if report.passed else "FAIL"
    print(
        f"{status} {report.path}: {report.algebra}; "
        f"generators={report.generator_count}, "
        f"constants={report.constant_count}, "
        f"parity_failures={report.parity_failures}, "
        f"anti-symmetry={report.antisymmetry_failures}/"
        f"{report.antisymmetry_checks} failures, "
        f"Jacobi={report.jacobi_failures}/{report.jacobi_checks} failures"
    )
    if report.samples:
        print("  Failure details for root-cause analysis:")
        for sample in report.samples:
            print(f"  - {sample}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check graded anti-symmetry, parity consistency, and the Super "
            "Jacobi identity using exact rational arithmetic."
        )
    )
    parser.add_argument(
        "files",
        nargs="*",
        type=Path,
        help="Schema 1 JSON files (default: data/C_1_structure.json through C_3)",
    )
    args = parser.parse_args()
    data_dir = Path(__file__).resolve().parent.parent / "data"
    paths = args.files or [
        data_dir / f"C_{n}_structure.json" for n in (1, 2, 3)
    ]

    failed = False
    for path in paths:
        try:
            report = verify_schema(path)
        except (OSError, json.JSONDecodeError, ValueError, TypeError) as error:
            print(f"ERROR {path}: {error}", file=sys.stderr)
            failed = True
            continue
        _print_report(report)
        failed = failed or not report.passed
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
