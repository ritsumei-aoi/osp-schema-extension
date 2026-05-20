from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any


@dataclass
class VerificationSummary:
    file: str
    n: int
    basis_size: int
    pair_checks: int
    triple_checks: int
    antisymmetry_failures: list[dict[str, Any]]
    jacobi_failures: list[dict[str, Any]]

    @property
    def passed(self) -> bool:
        return not self.antisymmetry_failures and not self.jacobi_failures


def parse_fraction(value: str) -> Fraction:
    return Fraction(value)


def basis_order(schema: dict[str, Any]) -> list[str]:
    return list(schema["basis"]["odd"]) + list(schema["basis"]["even"])


def parity_map(schema: dict[str, Any]) -> dict[str, int]:
    return dict(schema["parity"])


def structure_lookup(schema: dict[str, Any]) -> dict[tuple[str, str], dict[str, Fraction]]:
    lookup: dict[tuple[str, str], dict[str, Fraction]] = {}
    for entry in schema["structure_constants"]:
        key = (entry["X"], entry["Y"])
        bucket = lookup.setdefault(key, {})
        coeff = bucket.get(entry["Z"], Fraction(0)) + parse_fraction(entry["coeff"])
        if coeff:
            bucket[entry["Z"]] = coeff
        elif entry["Z"] in bucket:
            del bucket[entry["Z"]]
    return lookup


def clean_map(values: dict[str, Fraction]) -> dict[str, Fraction]:
    return {name: coeff for name, coeff in values.items() if coeff}


def add_scaled_map(target: dict[str, Fraction], source: dict[str, Fraction], scale: Fraction) -> None:
    for name, coeff in source.items():
        new_coeff = target.get(name, Fraction(0)) + coeff * scale
        if new_coeff:
            target[name] = new_coeff
        elif name in target:
            del target[name]


def bracket_of_pair(
    lookup: dict[tuple[str, str], dict[str, Fraction]], left: str, right: str
) -> dict[str, Fraction]:
    return dict(lookup.get((left, right), {}))


def bracket_linear(
    lookup: dict[tuple[str, str], dict[str, Fraction]],
    left: dict[str, Fraction],
    right: dict[str, Fraction],
) -> dict[str, Fraction]:
    result: dict[str, Fraction] = {}
    for left_name, left_coeff in left.items():
        for right_name, right_coeff in right.items():
            add_scaled_map(
                result,
                bracket_of_pair(lookup, left_name, right_name),
                left_coeff * right_coeff,
            )
    return clean_map(result)


def format_coeff_map(values: dict[str, Fraction]) -> dict[str, str]:
    return {name: str(coeff) for name, coeff in sorted(values.items())}


def verify_antisymmetry(
    schema: dict[str, Any],
    lookup: dict[tuple[str, str], dict[str, Fraction]],
    max_failures: int,
) -> tuple[int, list[dict[str, Any]]]:
    basis = basis_order(schema)
    parity = parity_map(schema)
    failures: list[dict[str, Any]] = []
    checks = 0

    for left in basis:
        for right in basis:
            checks += 1
            lhs = bracket_of_pair(lookup, left, right)
            rhs = bracket_of_pair(lookup, right, left)
            expected: dict[str, Fraction] = {}
            scale = Fraction(-((-1) ** (parity[left] * parity[right])))
            add_scaled_map(expected, rhs, scale)
            expected = clean_map(expected)
            if lhs != expected and len(failures) < max_failures:
                failures.append(
                    {
                        "left": left,
                        "right": right,
                        "actual": format_coeff_map(lhs),
                        "expected": format_coeff_map(expected),
                    }
                )

    return checks, failures


def verify_super_jacobi(
    schema: dict[str, Any],
    lookup: dict[tuple[str, str], dict[str, Fraction]],
    max_failures: int,
) -> tuple[int, list[dict[str, Any]]]:
    basis = basis_order(schema)
    parity = parity_map(schema)
    failures: list[dict[str, Any]] = []
    checks = 0

    for left in basis:
        left_map = {left: Fraction(1)}
        for middle in basis:
            middle_map = {middle: Fraction(1)}
            for right in basis:
                right_map = {right: Fraction(1)}
                checks += 1

                yz = bracket_linear(lookup, middle_map, right_map)
                zx = bracket_linear(lookup, right_map, left_map)
                xy = bracket_linear(lookup, left_map, middle_map)

                term_one = bracket_linear(lookup, left_map, yz)
                term_two = bracket_linear(lookup, middle_map, zx)
                term_three = bracket_linear(lookup, right_map, xy)

                jacobi: dict[str, Fraction] = {}
                add_scaled_map(
                    jacobi,
                    term_one,
                    Fraction((-1) ** (parity[left] * parity[right])),
                )
                add_scaled_map(
                    jacobi,
                    term_two,
                    Fraction((-1) ** (parity[middle] * parity[left])),
                )
                add_scaled_map(
                    jacobi,
                    term_three,
                    Fraction((-1) ** (parity[right] * parity[middle])),
                )
                jacobi = clean_map(jacobi)

                if jacobi and len(failures) < max_failures:
                    failures.append(
                        {
                            "left": left,
                            "middle": middle,
                            "right": right,
                            "jacobi": format_coeff_map(jacobi),
                        }
                    )

    return checks, failures


def verify_schema(path: Path, max_failures: int = 10) -> VerificationSummary:
    schema = json.loads(path.read_text(encoding="utf-8"))
    lookup = structure_lookup(schema)
    pair_checks, antisymmetry_failures = verify_antisymmetry(schema, lookup, max_failures)
    triple_checks, jacobi_failures = verify_super_jacobi(schema, lookup, max_failures)

    return VerificationSummary(
        file=path.name,
        n=int(schema["algebra"]["n"]),
        basis_size=len(basis_order(schema)),
        pair_checks=pair_checks,
        triple_checks=triple_checks,
        antisymmetry_failures=antisymmetry_failures,
        jacobi_failures=jacobi_failures,
    )


def format_summary(summary: VerificationSummary) -> str:
    lines = [
        f"{summary.file}: {'PASS' if summary.passed else 'FAIL'}",
        f"  n={summary.n}, basis={summary.basis_size}, pair_checks={summary.pair_checks}, triple_checks={summary.triple_checks}",
        f"  anti_symmetry_failures={len(summary.antisymmetry_failures)}, jacobi_failures={len(summary.jacobi_failures)}",
    ]
    if summary.antisymmetry_failures:
        lines.append("  first anti-symmetry failure:")
        lines.append(f"    {json.dumps(summary.antisymmetry_failures[0], ensure_ascii=False)}")
    if summary.jacobi_failures:
        lines.append("  first Jacobi failure:")
        lines.append(f"    {json.dumps(summary.jacobi_failures[0], ensure_ascii=False)}")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify C(n+1) structure constants from generated JSON.")
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Specific JSON files to verify (defaults to data/C_1_structure.json ... C_3_structure.json)",
    )
    parser.add_argument("--max-failures", type=int, default=10, help="Maximum stored failures per check type")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = args.paths or [Path("data") / f"C_{n}_structure.json" for n in (1, 2, 3)]

    overall_passed = True
    for path in paths:
        summary = verify_schema(path, max_failures=args.max_failures)
        print(format_summary(summary))
        overall_passed = overall_passed and summary.passed

    if not overall_passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
