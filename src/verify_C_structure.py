#!/usr/bin/env python3
"""Verify graded antisymmetry and super-Jacobi for generated C(n+1) data."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


def _add_scaled(target: dict[str, Fraction], source: dict[str, Fraction],
                scale: Fraction) -> None:
    for label, coeff in source.items():
        target[label] = target.get(label, Fraction()) + scale * coeff
        if not target[label]:
            del target[label]


def verify_schema(schema: dict[str, Any]) -> tuple[list[str], dict[str, int]]:
    errors: list[str] = []
    basis = schema.get("basis", {})
    labels = basis.get("even", []) + basis.get("odd", [])
    parity = schema.get("parity", {})
    if len(labels) != len(set(labels)):
        errors.append("basis contains duplicate generator labels")
    if set(labels) != set(parity):
        errors.append("parity keys do not match basis labels")
    realization_labels = set(
        schema.get("generator_realization", {}).get("realizations", {})
    )
    if realization_labels != set(labels):
        errors.append("realization labels do not match basis labels")
    if any(parity.get(label) != 0 for label in basis.get("even", [])):
        errors.append("even basis contains a non-even parity")
    if any(parity.get(label) != 1 for label in basis.get("odd", [])):
        errors.append("odd basis contains a non-odd parity")

    order = {label: index for index, label in enumerate(labels)}
    entries: dict[tuple[str, str], dict[str, Fraction]] = {}
    raw_constants = schema.get("structure_constants", [])
    for row_number, row in enumerate(raw_constants, start=1):
        x, y, z = row.get("X"), row.get("Y"), row.get("Z")
        if x not in order or y not in order or z not in order:
            errors.append(f"structure constant {row_number} references an unknown generator")
            continue
        if order[x] > order[y]:
            errors.append(f"structure constant {row_number} is not in canonical pair order")
        key = (x, y)
        if z in entries.setdefault(key, {}):
            errors.append(f"duplicate structure constant for [{x}, {y}] -> {z}")
            continue
        try:
            coeff = Fraction(row["coeff"])
        except (KeyError, ValueError, ZeroDivisionError):
            errors.append(f"structure constant {row_number} has an invalid coefficient")
            continue
        if not coeff:
            errors.append(f"structure constant {row_number} has zero coefficient")
        entries[key][z] = coeff
        if row.get("sign_rule") != "graded":
            errors.append(f"structure constant {row_number} lacks the graded sign rule")
        if parity.get(z) != (parity.get(x, 0) ^ parity.get(y, 0)):
            errors.append(f"structure constant {row_number} violates parity")

    def bracket(x: str, y: str) -> dict[str, Fraction]:
        direct = entries.get((x, y))
        if direct is not None:
            return direct
        reverse = entries.get((y, x), {})
        sign = -1 if parity.get(x, 0) and parity.get(y, 0) else 1
        return {label: -sign * coeff for label, coeff in reverse.items()}

    pair_checks = 0
    for x in labels:
        for y in labels:
            pair_checks += 1
            left = bracket(x, y)
            right = {}
            sign = -1 if parity.get(x, 0) and parity.get(y, 0) else 1
            _add_scaled(right, bracket(y, x), Fraction(-sign))
            if left != right:
                errors.append(f"graded antisymmetry fails for ({x}, {y})")
                break

    triple_checks = 0
    for x in labels:
        for y in labels:
            for z in labels:
                triple_checks += 1
                total: dict[str, Fraction] = {}
                terms = (
                    ((-1) ** (parity.get(x, 0) * parity.get(z, 0)), x, y, z),
                    ((-1) ** (parity.get(y, 0) * parity.get(x, 0)), y, z, x),
                    ((-1) ** (parity.get(z, 0) * parity.get(y, 0)), z, x, y),
                )
                for sign, outer_left, inner_left, inner_right in terms:
                    for middle, inner_coeff in bracket(inner_left, inner_right).items():
                        _add_scaled(
                            total,
                            bracket(outer_left, middle),
                            Fraction(sign) * inner_coeff,
                        )
                if total:
                    errors.append(f"super-Jacobi fails for ({x}, {y}, {z}): {total}")
                    break
            if errors and errors[-1].startswith("super-Jacobi fails"):
                break
        if errors and errors[-1].startswith("super-Jacobi fails"):
            break

    return errors, {
        "generators": len(labels),
        "structure_constants": len(raw_constants),
        "pair_checks": pair_checks,
        "triple_checks": triple_checks,
    }


def verify_file(path: Path) -> tuple[list[str], dict[str, int]]:
    schema = json.loads(path.read_text(encoding="utf-8"))
    return verify_schema(schema)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data",
    )
    parser.add_argument("--ranks", type=int, nargs="+", default=(1, 2, 3))
    args = parser.parse_args()
    failures = 0
    for n in args.ranks:
        path = args.data_dir / f"C_{n}_structure.json"
        try:
            errors, stats = verify_file(path)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"C_{n}: FAIL — unable to load {path}: {exc}")
            failures += 1
            continue
        if errors:
            print(f"C_{n}: FAIL — {len(errors)} issue(s)")
            for error in errors:
                print(f"  - {error}")
            failures += 1
        else:
            print(
                f"C_{n}: PASS — {stats['generators']} generators, "
                f"{stats['structure_constants']} constants, "
                f"{stats['pair_checks']} ordered pairs, "
                f"{stats['triple_checks']} ordered triples"
            )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
