#!/usr/bin/env python3
"""Verify graded antisymmetry and Super Jacobi for generated C schemas."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Mapping


Bracket = dict[str, Fraction]
BracketTable = dict[tuple[str, str], Bracket]


def _add(left: Mapping[str, Fraction], right: Mapping[str, Fraction]) -> Bracket:
    result = defaultdict(Fraction, left)
    for label, coefficient in right.items():
        result[label] += coefficient
    return {label: coefficient for label, coefficient in result.items() if coefficient}


def _scale(value: Mapping[str, Fraction], coefficient: Fraction | int) -> Bracket:
    return {
        label: coefficient * scalar
        for label, scalar in value.items()
        if coefficient * scalar
    }


def _ordered_labels(schema: dict) -> list[str]:
    labels = list(schema["generator_realization"]["realizations"])
    basis_labels = schema["basis"]["even"] + schema["basis"]["odd"]
    if len(labels) != len(set(labels)) or set(labels) != set(basis_labels):
        raise ValueError("Realization labels do not match the basis labels")
    return labels


def verify_schema(schema: dict) -> dict[str, int]:
    labels = _ordered_labels(schema)
    positions = {label: index for index, label in enumerate(labels)}
    parity = schema["parity"]
    if set(parity) != set(labels):
        raise ValueError("Parity map does not match the basis")

    canonical: BracketTable = {}
    seen: set[tuple[str, str, str]] = set()
    for entry in schema["structure_constants"]:
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        if x not in positions or y not in positions or z not in positions:
            raise ValueError(f"Structure constant uses an unknown generator: {entry}")
        if positions[x] > positions[y]:
            raise ValueError(f"Non-canonical bracket pair in record: {entry}")
        record_key = (x, y, z)
        if record_key in seen:
            raise ValueError(f"Duplicate structure-constant record: {entry}")
        seen.add(record_key)
        coefficient = Fraction(entry["coeff"])
        if not coefficient:
            raise ValueError(f"Zero coefficient stored in structure constants: {entry}")
        pair = (x, y)
        result = canonical.setdefault(pair, {})
        result[z] = result.get(z, Fraction()) + coefficient

    def bracket(x: str, y: str) -> Bracket:
        if positions[x] <= positions[y]:
            return canonical.get((x, y), {})
        reverse = canonical.get((y, x), {})
        sign = 1 if parity[x] and parity[y] else -1
        return _scale(reverse, sign)

    pair_checks = 0
    for x in labels:
        for y in labels:
            sign = -1 if parity[x] and parity[y] else 1
            if _add(bracket(x, y), _scale(bracket(y, x), sign)):
                raise ValueError(f"Graded antisymmetry failed for ({x}, {y})")
            pair_checks += 1

    def bracket_vector(generator: str, value: Mapping[str, Fraction]) -> Bracket:
        result: Bracket = {}
        for other, coefficient in value.items():
            result = _add(
                result,
                _scale(bracket(generator, other), coefficient),
            )
        return result

    triple_checks = 0
    for x in labels:
        for y in labels:
            for z in labels:
                yz = bracket(y, z)
                zx = bracket(z, x)
                xy = bracket(x, y)
                first = bracket_vector(x, yz)
                second = bracket_vector(y, zx)
                third = bracket_vector(z, xy)
                first_sign = -1 if parity[x] and parity[z] else 1
                second_sign = -1 if parity[y] and parity[x] else 1
                third_sign = -1 if parity[z] and parity[y] else 1
                jacobi = _add(
                    _add(_scale(first, first_sign), _scale(second, second_sign)),
                    _scale(third, third_sign),
                )
                if jacobi:
                    raise ValueError(
                        f"Super Jacobi failed for ({x}, {y}, {z}): {jacobi}"
                    )
                triple_checks += 1

    return {
        "generators": len(labels),
        "pair_checks": pair_checks,
        "triple_checks": triple_checks,
        "stored_bracket_records": len(schema["structure_constants"]),
    }


def verify_file(path: Path) -> dict[str, int]:
    with path.open(encoding="utf-8") as stream:
        schema = json.load(stream)
    return verify_schema(schema)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--ranks", type=int, nargs="+", default=[1, 2, 3])
    args = parser.parse_args()

    failed = False
    for rank in args.ranks:
        path = args.data_dir / f"C_{rank}_structure.json"
        try:
            result = verify_file(path)
        except (OSError, json.JSONDecodeError, KeyError, ValueError) as error:
            print(f"C_{rank}: FAIL ({error})", file=sys.stderr)
            failed = True
            continue
        print(
            f"C_{rank}: PASS; generators={result['generators']}, "
            f"pairs={result['pair_checks']}, triples={result['triple_checks']}, "
            f"bracket_records={result['stored_bracket_records']}"
        )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
