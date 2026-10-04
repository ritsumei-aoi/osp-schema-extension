#!/usr/bin/env python3
"""Verify graded skew-symmetry and the super Jacobi identity in C schemas."""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

Bracket = dict[str, Fraction]


def _read_structure(path: Path) -> tuple[list[str], dict[str, int], dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    basis = data["basis"]["odd"] + data["basis"]["even"]
    parity = data["parity"]
    if len(set(basis)) != len(basis) or set(basis) != set(parity):
        raise ValueError(f"{path}: basis and parity labels do not match")

    positions = {label: index for index, label in enumerate(basis)}
    canonical: dict[tuple[str, str], Bracket] = {}
    for record in data["structure_constants"]:
        x, y, z = record["X"], record["Y"], record["Z"]
        if x not in positions or y not in positions or z not in positions:
            raise ValueError(f"{path}: bracket record references an unknown generator")
        if positions[x] > positions[y]:
            raise ValueError(f"{path}: non-canonical input pair ({x}, {y})")
        if record["sign_rule"] != "graded":
            raise ValueError(f"{path}: unsupported sign rule {record['sign_rule']!r}")
        coefficient = Fraction(record["coeff"])
        if not coefficient:
            raise ValueError(f"{path}: zero coefficient stored for ({x}, {y}, {z})")
        key = (x, y)
        output = canonical.setdefault(key, {})
        if z in output:
            raise ValueError(f"{path}: duplicate output term for ({x}, {y}, {z})")
        output[z] = coefficient

    return basis, parity, canonical


def _directed_bracket(
    x: str,
    y: str,
    parity: dict[str, int],
    canonical: dict[tuple[str, str], Bracket],
    positions: dict[str, int],
) -> Bracket:
    if positions[x] <= positions[y]:
        return canonical.get((x, y), {})
    sign = -1 if parity[x] * parity[y] == 0 else 1
    return {
        output: sign * coefficient
        for output, coefficient in canonical.get((y, x), {}).items()
    }


def _add_scaled(target: Bracket, source: Bracket, factor: Fraction) -> None:
    for label, coefficient in source.items():
        value = target.get(label, Fraction(0)) + factor * coefficient
        if value:
            target[label] = value
        else:
            target.pop(label, None)


def verify_file(path: Path) -> list[str]:
    basis, parity, canonical = _read_structure(path)
    positions = {label: index for index, label in enumerate(basis)}
    issues: list[str] = []

    for x in basis:
        for y in basis:
            xy = _directed_bracket(x, y, parity, canonical, positions)
            yx = _directed_bracket(y, x, parity, canonical, positions)
            skew = dict(xy)
            _add_scaled(
                skew,
                yx,
                Fraction(1 if parity[x] * parity[y] == 0 else -1),
            )
            if skew:
                issues.append(f"graded skew-symmetry fails for ({x}, {y}): {skew}")

    for x in basis:
        for y in basis:
            for z in basis:
                jacobi: Bracket = {}
                terms = (
                    (
                        -1 if parity[x] * parity[z] else 1,
                        y,
                        z,
                        x,
                    ),
                    (
                        -1 if parity[y] * parity[x] else 1,
                        z,
                        x,
                        y,
                    ),
                    (
                        -1 if parity[z] * parity[y] else 1,
                        x,
                        y,
                        z,
                    ),
                )
                for sign, inner_x, inner_y, outer_x in terms:
                    inner = _directed_bracket(
                        inner_x, inner_y, parity, canonical, positions
                    )
                    for middle, inner_coefficient in inner.items():
                        outer = _directed_bracket(
                            outer_x, middle, parity, canonical, positions
                        )
                        _add_scaled(
                            jacobi,
                            outer,
                            Fraction(sign) * inner_coefficient,
                        )
                if jacobi:
                    issues.append(
                        f"super Jacobi fails for ({x}, {y}, {z}): {jacobi}"
                    )
                    if len(issues) >= 20:
                        return issues
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    args = parser.parse_args()

    failed = False
    for n in (1, 2, 3):
        path = args.data_dir / f"C_{n}_structure.json"
        try:
            data: Any = json.loads(path.read_text(encoding="utf-8"))
            basis, _, canonical = _read_structure(path)
            issues = verify_file(path)
            if issues:
                failed = True
                print(f"FAIL {path}: {len(issues)} violation(s)")
                for issue in issues:
                    print(f"  {issue}")
            else:
                pair_checks = len(basis) ** 2
                triple_checks = len(basis) ** 3
                print(
                    f"PASS {path}: {pair_checks} pair checks, "
                    f"{triple_checks} triple checks, "
                    f"{len(data['structure_constants'])} nonzero records "
                    f"({len(canonical)} nonzero input pairs)"
                )
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            failed = True
            print(f"FAIL {path}: {exc}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
