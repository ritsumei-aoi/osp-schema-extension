#!/usr/bin/env python3
"""Verify graded antisymmetry and the super Jacobi identity in C structure files."""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any


def _fraction(value: str) -> Fraction:
    try:
        return Fraction(value)
    except (TypeError, ValueError, ZeroDivisionError) as error:
        raise ValueError(f"Invalid rational structure constant: {value!r}") from error


def verify_schema(schema: dict[str, Any]) -> dict[str, Any]:
    basis = schema.get("basis", {})
    generators = basis.get("even", []) + basis.get("odd", [])
    parity = schema.get("parity", {})
    if len(generators) != len(set(generators)):
        raise ValueError("Basis contains duplicate generator labels")
    if set(parity) != set(generators):
        raise ValueError("Parity map does not cover exactly the basis generators")
    if any(parity[name] not in (0, 1) for name in generators):
        raise ValueError("Parity values must be 0 or 1")

    indices = {name: index for index, name in enumerate(generators)}
    constants: dict[tuple[str, str], dict[str, Fraction]] = {}
    errors: list[str] = []
    for entry in schema.get("structure_constants", []):
        x, y, z = entry.get("X"), entry.get("Y"), entry.get("Z")
        if x not in indices or y not in indices or z not in indices:
            errors.append(f"Unknown generator in structure constant {entry!r}")
            continue
        if indices[x] > indices[y]:
            errors.append(f"Noncanonical pair order in structure constant {x}, {y}")
        pair = (x, y)
        components = constants.setdefault(pair, {})
        if z in components:
            errors.append(f"Duplicate component [{x}, {y}] -> {z}")
            continue
        coeff = _fraction(entry.get("coeff"))
        if coeff == 0:
            errors.append(f"Zero coefficient recorded for [{x}, {y}] -> {z}")
            continue
        components[z] = coeff
        if parity[z] != (parity[x] + parity[y]) % 2:
            errors.append(f"Parity mismatch in [{x}, {y}] -> {z}")

    def bracket(x: str, y: str) -> dict[str, Fraction]:
        if indices[x] <= indices[y]:
            return constants.get((x, y), {})
        sign = -1 if parity[x] * parity[y] else 1
        return {
            z: -sign * coeff
            for z, coeff in constants.get((y, x), {}).items()
        }

    pair_checks = 0
    for x in generators:
        for y in generators:
            pair_checks += 1
            forward, reverse = bracket(x, y), bracket(y, x)
            sign = -1 if parity[x] * parity[y] else 1
            combined = dict(forward)
            for z, coeff in reverse.items():
                combined[z] = combined.get(z, Fraction()) + sign * coeff
            if any(combined.values()):
                errors.append(f"Graded antisymmetry fails for ({x}, {y}): {combined}")

    jacobi_checks = 0
    for x in generators:
        for y in generators:
            for z in generators:
                jacobi_checks += 1
                terms: dict[str, Fraction] = {}
                cyclic = (
                    (x, y, z, parity[x] * parity[z]),
                    (y, z, x, parity[y] * parity[x]),
                    (z, x, y, parity[z] * parity[y]),
                )
                for first, second, third, exponent in cyclic:
                    sign = -1 if exponent % 2 else 1
                    for intermediate, inner_coeff in bracket(second, third).items():
                        for result, outer_coeff in bracket(first, intermediate).items():
                            terms[result] = (
                                terms.get(result, Fraction())
                                + sign * inner_coeff * outer_coeff
                            )
                terms = {name: coeff for name, coeff in terms.items() if coeff}
                if terms:
                    errors.append(f"Super Jacobi fails for ({x}, {y}, {z}): {terms}")

    return {
        "algebra": schema.get("algebra", {}).get("cartan_type", "unknown"),
        "generator_count": len(generators),
        "pair_checks": pair_checks,
        "jacobi_checks": jacobi_checks,
        "passed": not errors,
        "errors": errors,
    }


def verify_file(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as source:
        schema = json.load(source)
    result = verify_schema(schema)
    result["file"] = path.name
    return result


def main(paths: list[str] | None = None) -> int:
    if paths is None:
        data_dir = Path(__file__).resolve().parents[1] / "data"
        paths = [str(data_dir / f"C_{n}_structure.json") for n in (1, 2, 3)]
    failed = False
    for filename in paths:
        path = Path(filename)
        try:
            result = verify_file(path)
        except (OSError, json.JSONDecodeError, ValueError) as error:
            print(f"FAIL {path}: {error}")
            failed = True
            continue
        status = "PASS" if result["passed"] else "FAIL"
        print(
            f"{status} {result['file']} ({result['algebra']}): "
            f"{result['generator_count']} generators, "
            f"{result['pair_checks']} pair checks, "
            f"{result['jacobi_checks']} Jacobi triples"
        )
        for error in result["errors"]:
            print(f"  {error}")
        failed |= not result["passed"]
    return int(failed)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or None))
