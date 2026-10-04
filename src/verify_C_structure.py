"""Verify graded antisymmetry and the super Jacobi identity from Schema 1 JSON."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


def verify_schema(schema: dict[str, Any]) -> dict[str, Any]:
    basis = schema["basis"]
    labels = basis["odd"] + basis["even"]
    label_set = set(labels)
    parity = schema["parity"]
    errors: list[str] = []
    if len(labels) != len(label_set):
        errors.append("Basis contains duplicate labels.")
    if set(parity) != label_set:
        errors.append("Parity keys do not exactly match basis labels.")

    position = {label: index for index, label in enumerate(labels)}
    bracket_table: dict[tuple[str, str], dict[str, Fraction]] = {}
    for entry in schema["structure_constants"]:
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        if x not in label_set or y not in label_set or z not in label_set:
            errors.append(f"Bracket references an unknown generator: {entry}.")
            continue
        if position[x] > position[y]:
            errors.append(f"Bracket pair is not in PBW order: ({x}, {y}).")
            continue
        if entry["sign_rule"] != "graded":
            errors.append(f"Bracket has invalid sign_rule: {entry}.")
        coefficient = Fraction(entry["coeff"])
        if not coefficient:
            errors.append(f"Explicit zero bracket coefficient: {entry}.")
        pair = (x, y)
        values = bracket_table.setdefault(pair, {})
        if z in values:
            errors.append(f"Duplicate structure constant for ({x}, {y}, {z}).")
        values[z] = coefficient
        if parity[z] != (parity[x] + parity[y]) % 2:
            errors.append(f"Bracket has incorrect parity: ({x}, {y}) -> {z}.")

    def bracket(x: str, y: str) -> dict[str, Fraction]:
        if position[x] <= position[y]:
            return bracket_table.get((x, y), {})
        factor = Fraction(-1 if not (parity[x] and parity[y]) else 1)
        return {
            z: factor * coefficient
            for z, coefficient in bracket_table.get((y, x), {}).items()
        }

    antisymmetry_pairs = 0
    for x in labels:
        for y in labels:
            antisymmetry_pairs += 1
            sign = Fraction(-1 if parity[x] and parity[y] else 1)
            residual = _add_vectors(bracket(x, y), bracket(y, x), sign)
            if residual:
                errors.append(f"Graded antisymmetry fails for ({x}, {y}): {residual}.")

    jacobi_triples = 0
    for x in labels:
        for y in labels:
            for z in labels:
                jacobi_triples += 1
                terms = (
                    (bracket(x, y), z, -1 if parity[x] * parity[z] else 1),
                    (bracket(y, z), x, -1 if parity[y] * parity[x] else 1),
                    (bracket(z, x), y, -1 if parity[z] * parity[y] else 1),
                )
                jacobi: dict[str, Fraction] = {}
                for inner, outer, sign in terms:
                    for middle, coefficient in inner.items():
                        for result, outer_coefficient in bracket(middle, outer).items():
                            jacobi[result] = jacobi.get(result, Fraction(0)) + (
                                sign * coefficient * outer_coefficient
                            )
                jacobi = {label: coeff for label, coeff in jacobi.items() if coeff}
                if jacobi:
                    errors.append(f"Super Jacobi fails for ({x}, {y}, {z}): {jacobi}.")

    return {
        "passed": not errors,
        "generator_count": len(labels),
        "structure_constant_count": len(schema["structure_constants"]),
        "antisymmetry_pairs": antisymmetry_pairs,
        "jacobi_triples": jacobi_triples,
        "errors": errors,
    }


def _add_vectors(
    left: dict[str, Fraction],
    right: dict[str, Fraction],
    right_scale: Fraction = Fraction(1),
) -> dict[str, Fraction]:
    result = dict(left)
    for label, coefficient in right.items():
        result[label] = result.get(label, Fraction(0)) + right_scale * coefficient
    return {label: coefficient for label, coefficient in result.items() if coefficient}


def verify_file(path: Path) -> dict[str, Any]:
    schema = json.loads(path.read_text(encoding="utf-8"))
    result = verify_schema(schema)
    result["file"] = str(path)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "files",
        nargs="*",
        type=Path,
        default=[
            Path(__file__).resolve().parent.parent / "data" / f"C_{n}_structure.json"
            for n in (1, 2, 3)
        ],
    )
    args = parser.parse_args()
    failed = False
    for path in args.files:
        result = verify_file(path)
        status = "PASS" if result["passed"] else "FAIL"
        print(
            f"{status} {result['file']}: generators={result['generator_count']}, "
            f"structure_constants={result['structure_constant_count']}, "
            f"ordered_pairs={result['antisymmetry_pairs']}, "
            f"triples={result['jacobi_triples']}"
        )
        for error in result["errors"]:
            print(f"  {error}")
        failed = failed or not result["passed"]
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
