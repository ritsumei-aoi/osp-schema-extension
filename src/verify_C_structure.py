"""Verify graded antisymmetry and super Jacobi for generated C structure data."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path


ScalarMap = dict[str, Fraction]


def _add_scaled(target: ScalarMap, source: ScalarMap, scale: Fraction) -> None:
    for generator, coefficient in source.items():
        target[generator] = target.get(generator, Fraction(0)) + scale * coefficient
        if not target[generator]:
            del target[generator]


def verify_file(path: Path) -> dict:
    data = json.loads(path.read_text())
    basis = data["basis"]["even"] + data["basis"]["odd"]
    parity = data["parity"]
    brackets: dict[tuple[str, str], ScalarMap] = defaultdict(dict)
    for entry in data["structure_constants"]:
        result = brackets[(entry["X"], entry["Y"])]
        result[entry["Z"]] = result.get(entry["Z"], Fraction(0)) + Fraction(entry["coeff"])

    antisymmetry_failures = []
    for x in basis:
        for y in basis:
            combined: ScalarMap = {}
            _add_scaled(combined, brackets[(x, y)], Fraction(1))
            _add_scaled(combined, brackets[(y, x)], Fraction((-1) ** (parity[x] * parity[y])))
            if combined:
                antisymmetry_failures.append((x, y, combined))

    def bracket_linear(generator: str, expression: ScalarMap) -> ScalarMap:
        result: ScalarMap = {}
        for other, coefficient in expression.items():
            _add_scaled(result, brackets[(generator, other)], coefficient)
        return result

    jacobi_failures = []
    for x in basis:
        for y in basis:
            for z in basis:
                terms: ScalarMap = {}
                sign_xyz = (-1) ** (parity[x] * parity[z])
                sign_yzx = (-1) ** (parity[y] * parity[x])
                sign_zxy = (-1) ** (parity[z] * parity[y])
                _add_scaled(terms, bracket_linear(x, brackets[(y, z)]), Fraction(sign_xyz))
                _add_scaled(terms, bracket_linear(y, brackets[(z, x)]), Fraction(sign_yzx))
                _add_scaled(terms, bracket_linear(z, brackets[(x, y)]), Fraction(sign_zxy))
                if terms:
                    jacobi_failures.append((x, y, z, terms))

    return {
        "file": path.name,
        "generators": len(basis),
        "pairs_checked": len(basis) ** 2,
        "triples_checked": len(basis) ** 3,
        "antisymmetry_failures": antisymmetry_failures,
        "jacobi_failures": jacobi_failures,
    }


def verify_all(data_dir: Path) -> list[dict]:
    return [verify_file(data_dir / f"C_{n}_structure.json") for n in (1, 2, 3)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    args = parser.parse_args()
    failed = False
    for result in verify_all(args.data_dir):
        antisymmetry_count = len(result["antisymmetry_failures"])
        jacobi_count = len(result["jacobi_failures"])
        passed = not antisymmetry_count and not jacobi_count
        failed |= not passed
        print(
            f"{result['file']}: {'PASS' if passed else 'FAIL'}; "
            f"{result['generators']} generators, {result['pairs_checked']} pairs, "
            f"{result['triples_checked']} triples; "
            f"antisymmetry failures={antisymmetry_count}, Jacobi failures={jacobi_count}"
        )
        for x, y, error in result["antisymmetry_failures"][:3]:
            print(f"  antisymmetry [{x},{y}]: {error}")
        for x, y, z, error in result["jacobi_failures"][:3]:
            print(f"  Jacobi ({x},{y},{z}): {error}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
