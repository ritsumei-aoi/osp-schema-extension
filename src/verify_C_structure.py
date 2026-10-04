#!/usr/bin/env python3
"""Verify graded antisymmetry and super-Jacobi for generated C structure files."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import TypeAlias


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
Vector: TypeAlias = dict[str, Fraction]
BracketTable: TypeAlias = dict[tuple[str, str], Vector]


def _load_schema(rank: int, data_dir: Path) -> dict[str, object]:
    path = data_dir / f"C_{rank}_structure.json"
    with path.open(encoding="utf-8") as stream:
        schema = json.load(stream)
    if schema["schema_version"] != "5.0" or schema["algebra"]["n"] != rank:
        raise ValueError(f"{path} does not contain a matching Schema 1 record")
    return schema


def _bracket_table(
    schema: dict[str, object], basis: list[str]
) -> BracketTable:
    index = {label: position for position, label in enumerate(basis)}
    table: BracketTable = {}
    for entry in schema["structure_constants"]:
        left, right, output = entry["X"], entry["Y"], entry["Z"]
        if left not in index or right not in index or output not in index:
            raise ValueError(f"Structure constant references an unknown generator: {entry}")
        if index[left] > index[right]:
            raise ValueError(f"Non-canonical structure-constant pair: {left}, {right}")
        key = left, right
        vector = table.setdefault(key, {})
        vector[output] = vector.get(output, Fraction(0)) + Fraction(entry["coeff"])
        if not vector[output]:
            del vector[output]
    return table


def _bracket(
    left: str,
    right: str,
    index: dict[str, int],
    parity: dict[str, int],
    table: BracketTable,
) -> Vector:
    if index[left] <= index[right]:
        return table.get((left, right), {})
    sign = -1 if (parity[left] * parity[right]) % 2 == 0 else 1
    return {
        output: sign * coefficient
        for output, coefficient in table.get((right, left), {}).items()
    }


def _add_scaled(target: Vector, source: Vector, scale: Fraction | int) -> None:
    for label, coefficient in source.items():
        target[label] = target.get(label, Fraction(0)) + scale * coefficient
        if not target[label]:
            del target[label]


def verify_schema(schema: dict[str, object]) -> dict[str, int]:
    realizations = schema["generator_realization"]["realizations"]
    basis = list(realizations)
    parity = schema["parity"]
    if set(basis) != set(parity):
        raise ValueError("Generator realization labels do not match the parity map")
    index = {label: position for position, label in enumerate(basis)}
    table = _bracket_table(schema, basis)
    antisymmetry_failures = 0
    jacobi_failures = 0

    for left in basis:
        for right in basis:
            forward = _bracket(left, right, index, parity, table)
            reverse = _bracket(right, left, index, parity, table)
            expected: Vector = {}
            _add_scaled(
                expected,
                forward,
                -1 if (parity[left] * parity[right]) % 2 == 0 else 1,
            )
            difference = dict(reverse)
            _add_scaled(difference, expected, -1)
            if difference:
                antisymmetry_failures += 1

    for x in basis:
        for y in basis:
            for z in basis:
                terms = (
                    (_nested(x, y, z, index, parity, table), (-1) ** (parity[x] * parity[z])),
                    (_nested(y, z, x, index, parity, table), (-1) ** (parity[y] * parity[x])),
                    (_nested(z, x, y, index, parity, table), (-1) ** (parity[z] * parity[y])),
                )
                jacobiator: Vector = {}
                for vector, sign in terms:
                    _add_scaled(jacobiator, vector, sign)
                if jacobiator:
                    jacobi_failures += 1

    return {
        "generators": len(basis),
        "pairs_checked": len(basis) ** 2,
        "triples_checked": len(basis) ** 3,
        "antisymmetry_failures": antisymmetry_failures,
        "jacobi_failures": jacobi_failures,
    }


def _nested(
    left: str,
    right: str,
    third: str,
    index: dict[str, int],
    parity: dict[str, int],
    table: BracketTable,
) -> Vector:
    result: Vector = {}
    for middle, coefficient in _bracket(right, third, index, parity, table).items():
        inner = _bracket(left, middle, index, parity, table)
        _add_scaled(result, inner, coefficient)
    return result


def main() -> int:
    passed = True
    for rank in (1, 2, 3):
        schema = _load_schema(rank, DATA_DIR)
        result = verify_schema(schema)
        status = (
            "PASS"
            if result["antisymmetry_failures"] == 0 and result["jacobi_failures"] == 0
            else "FAIL"
        )
        print(
            f"{status} C_{rank}: {result['generators']} generators, "
            f"{result['pairs_checked']} pairs, "
            f"{result['triples_checked']} triples; "
            f"antisymmetry failures={result['antisymmetry_failures']}, "
            f"Jacobi failures={result['jacobi_failures']}"
        )
        passed = passed and status == "PASS"
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
