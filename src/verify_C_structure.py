#!/usr/bin/env python3
"""Verify graded antisymmetry and super Jacobi for generated C structure data."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def load_structure(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        data = json.load(stream)
    if data["algebra"]["family"] != "C":
        raise ValueError(f"{path} does not contain a C-family algebra")
    return data


def verify_structure(data: dict[str, Any]) -> dict[str, int]:
    basis = data["basis"]["even"] + data["basis"]["odd"]
    positions = {label: index for index, label in enumerate(basis)}
    parities = data["parity"]
    if len(positions) != len(basis) or set(parities) != set(basis):
        raise ValueError("Basis labels must be unique and parity must cover exactly the basis")

    brackets: dict[tuple[str, str], dict[str, Fraction]] = {}
    for entry in data["structure_constants"]:
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        if x not in positions or y not in positions or z not in positions:
            raise ValueError(f"Structure constant references a non-basis label: {entry}")
        if positions[x] > positions[y]:
            raise ValueError(f"Stored bracket pair is not in canonical basis order: {x}, {y}")
        pair = (x, y)
        components = brackets.setdefault(pair, {})
        if z in components:
            raise ValueError(f"Duplicate structure constant for [{x}, {y}] -> {z}")
        components[z] = Fraction(entry["coeff"])

    def bracket(x: str, y: str) -> dict[str, Fraction]:
        if positions[x] <= positions[y]:
            return brackets.get((x, y), {})
        sign = -1 if parities[x] * parities[y] else 1
        return {
            z: -sign * coeff
            for z, coeff in brackets.get((y, x), {}).items()
        }

    pair_count = len(basis) ** 2
    for x, y in product(basis, repeat=2):
        expected_sign = -1 if parities[x] * parities[y] else 1
        forward = bracket(x, y)
        reverse = bracket(y, x)
        outputs = set(forward) | set(reverse)
        for z in outputs:
            if reverse.get(z, Fraction(0)) != -expected_sign * forward.get(z, Fraction(0)):
                raise ValueError(f"Graded antisymmetry failed for ({x}, {y}) at output {z}")

    def nested(x: str, y: str, z: str) -> dict[str, Fraction]:
        result: dict[str, Fraction] = {}
        for middle, inner_coeff in bracket(y, z).items():
            for output, outer_coeff in bracket(x, middle).items():
                result[output] = result.get(output, Fraction(0)) + inner_coeff * outer_coeff
        return {label: coeff for label, coeff in result.items() if coeff}

    triple_count = len(basis) ** 3
    for x, y, z in product(basis, repeat=3):
        sign_xz = -1 if parities[x] * parities[z] else 1
        sign_xy = -1 if parities[x] * parities[y] else 1
        sign_yz = -1 if parities[y] * parities[z] else 1
        total: dict[str, Fraction] = {}
        for sign, term in (
            (sign_xz, nested(x, y, z)),
            (sign_xy, nested(y, z, x)),
            (sign_yz, nested(z, x, y)),
        ):
            for output, coeff in term.items():
                total[output] = total.get(output, Fraction(0)) + sign * coeff
        nonzero = {label: coeff for label, coeff in total.items() if coeff}
        if nonzero:
            raise ValueError(f"Super Jacobi failed for ({x}, {y}, {z}): {nonzero}")
    return {"generators": len(basis), "ordered_pairs": pair_count, "ordered_triples": triple_count}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data")
    args = parser.parse_args()
    totals = {"generators": 0, "ordered_pairs": 0, "ordered_triples": 0}
    for n in (1, 2, 3):
        path = args.data_dir / f"C_{n}_structure.json"
        counts = verify_structure(load_structure(path))
        print(
            f"C_{n}: PASS — {counts['generators']} generators, "
            f"{counts['ordered_pairs']} ordered pairs checked for graded antisymmetry, "
            f"{counts['ordered_triples']} ordered triples checked for super Jacobi"
        )
        for key in totals:
            totals[key] += counts[key]
    print(
        f"TOTAL: PASS — {totals['ordered_pairs']} ordered pairs and "
        f"{totals['ordered_triples']} ordered triples checked"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
