#!/usr/bin/env python3
"""Verify C(n+1) structure-constant JSON by graded skew-symmetry and Jacobi."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path


def verify_schema(schema):
    basis = schema.get("basis", {})
    labels = list(schema.get("generator_realization", {}).get("realizations", {}))
    parity = schema.get("parity", {})
    if set(labels) != set(basis.get("even", []) + basis.get("odd", [])):
        raise ValueError("PBW realization labels and basis labels differ")
    if set(parity) != set(labels):
        raise ValueError("Parity map and basis labels differ")
    if any(parity[label] not in (0, 1) for label in labels):
        raise ValueError("Generator parity must be 0 or 1")

    order = {label: index for index, label in enumerate(labels)}
    raw = defaultdict(lambda: defaultdict(Fraction))
    seen = set()
    for entry in schema.get("structure_constants", []):
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        if x not in order or y not in order or z not in order:
            raise ValueError(f"Unknown generator in structure constant: {entry}")
        if order[x] > order[y]:
            raise ValueError(f"Non-canonical generator pair ordering: {x}, {y}")
        key = (x, y, z)
        if key in seen:
            raise ValueError(f"Duplicate structure-constant entry: {key}")
        seen.add(key)
        coeff = Fraction(entry["coeff"])
        if not coeff:
            raise ValueError(f"Stored zero structure constant: {key}")
        expected_parity = (parity[x] + parity[y]) % 2
        if parity[z] != expected_parity:
            raise ValueError(f"Parity mismatch in structure constant: {key}")
        raw[(x, y)][z] += coeff

    def bracket(x, y):
        if order[x] <= order[y]:
            return dict(raw.get((x, y), {}))
        sign = -1 if (parity[x] * parity[y]) % 2 == 0 else 1
        return {
            z: sign * coeff
            for z, coeff in raw.get((y, x), {}).items()
        }

    pair_checks = 0
    for x in labels:
        for y in labels:
            left = bracket(x, y)
            right = bracket(y, x)
            sign = -1 if (parity[x] * parity[y]) % 2 else 1
            if any(
                left.get(z, Fraction(0)) + sign * right.get(z, Fraction(0))
                for z in set(left) | set(right)
            ):
                raise ValueError(f"Graded skew-symmetry failed for ({x}, {y})")
            pair_checks += 1

    triple_checks = 0
    for x in labels:
        for y in labels:
            for z in labels:
                terms = defaultdict(Fraction)
                cyclic_terms = (
                    (
                        -1 if parity[x] * parity[z] % 2 else 1,
                        x,
                        y,
                        z,
                    ),
                    (
                        -1 if parity[y] * parity[x] % 2 else 1,
                        y,
                        z,
                        x,
                    ),
                    (
                        -1 if parity[z] * parity[y] % 2 else 1,
                        z,
                        x,
                        y,
                    ),
                )
                for sign, outer, first, second in cyclic_terms:
                    for middle, inner_coeff in bracket(first, second).items():
                        for result, outer_coeff in bracket(outer, middle).items():
                            terms[result] += sign * inner_coeff * outer_coeff
                if any(terms.values()):
                    raise ValueError(
                        f"Super-Jacobi failed for ({x}, {y}, {z}): "
                        f"{dict(terms)}"
                    )
                triple_checks += 1

    return {
        "generators": len(labels),
        "stored_constants": len(seen),
        "pair_checks": pair_checks,
        "triple_checks": triple_checks,
    }


def verify_file(path):
    with path.open(encoding="utf-8") as stream:
        schema = json.load(stream)
    return verify_schema(schema)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--ranks", nargs="+", type=int, default=[1, 2, 3])
    args = parser.parse_args(argv)
    data_dir = Path(args.data_dir)
    failures = 0
    for n in args.ranks:
        path = data_dir / f"C_{n}_structure.json"
        try:
            result = verify_file(path)
        except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
            failures += 1
            print(f"FAIL {path}: {error}")
            continue
        print(
            f"PASS {path}: {result['generators']} generators, "
            f"{result['stored_constants']} constants, "
            f"{result['pair_checks']} pairs, "
            f"{result['triple_checks']} triples"
        )
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
