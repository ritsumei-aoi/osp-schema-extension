"""Verify graded skew-symmetry and the super Jacobi identity for C datasets."""

from __future__ import annotations

import json
from fractions import Fraction
from itertools import product
from pathlib import Path


class StructureTable:
    def __init__(self, data: dict):
        self.data = data
        self.names = data["basis"]["odd"] + data["basis"]["even"]
        self.indices = {name: index for index, name in enumerate(self.names)}
        self.parity = data["parity"]
        self.brackets: dict[tuple[str, str], dict[str, Fraction]] = {}
        for entry in data["structure_constants"]:
            key = (entry["X"], entry["Y"])
            result = self.brackets.setdefault(key, {})
            result[entry["Z"]] = result.get(entry["Z"], Fraction(0)) + Fraction(
                entry["coeff"]
            )

    def bracket(self, x: str, y: str) -> dict[str, Fraction]:
        if self.indices[x] <= self.indices[y]:
            return self.brackets.get((x, y), {})
        sign = -1 if self.parity[x] * self.parity[y] == 0 else 1
        return {
            name: sign * coefficient
            for name, coefficient in self.brackets.get((y, x), {}).items()
        }

    def nested(self, x: str, inner: dict[str, Fraction]) -> dict[str, Fraction]:
        result: dict[str, Fraction] = {}
        for y, inner_coefficient in inner.items():
            for z, outer_coefficient in self.bracket(x, y).items():
                result[z] = result.get(z, Fraction(0)) + (
                    inner_coefficient * outer_coefficient
                )
                if not result[z]:
                    del result[z]
        return result


def verify(data: dict) -> dict[str, int | bool]:
    table = StructureTable(data)
    antisymmetry_checks = 0
    for x, y in product(table.names, repeat=2):
        left = table.bracket(x, y)
        right = table.bracket(y, x)
        sign = 1 if table.parity[x] * table.parity[y] == 0 else -1
        combined = dict(left)
        for name, coefficient in right.items():
            combined[name] = combined.get(name, Fraction(0)) + sign * coefficient
            if not combined[name]:
                del combined[name]
        if combined:
            raise AssertionError(
                f"Graded skew-symmetry failed for [{x},{y}]: {combined}"
            )
        antisymmetry_checks += 1

    jacobi_checks = 0
    for x, y, z in product(table.names, repeat=3):
        term1 = table.nested(x, table.bracket(y, z))
        term2 = table.nested(y, table.bracket(z, x))
        term3 = table.nested(z, table.bracket(x, y))
        result: dict[str, Fraction] = {}
        for term, exponent in (
            (term1, table.parity[x] * table.parity[z]),
            (term2, table.parity[y] * table.parity[x]),
            (term3, table.parity[z] * table.parity[y]),
        ):
            sign = -1 if exponent else 1
            for name, coefficient in term.items():
                result[name] = result.get(name, Fraction(0)) + sign * coefficient
                if not result[name]:
                    del result[name]
        if result:
            raise AssertionError(f"Super Jacobi failed for ({x},{y},{z}): {result}")
        jacobi_checks += 1
    return {
        "basis_generators": len(table.names),
        "antisymmetry_checks": antisymmetry_checks,
        "jacobi_checks": jacobi_checks,
        "passed": True,
    }


def verify_file(path: Path) -> dict[str, int | bool]:
    with path.open(encoding="utf-8") as source:
        return verify(json.load(source))


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    for rank in (1, 2, 3):
        dataset = root / "data" / f"C_{rank}_structure.json"
        try:
            report = verify_file(dataset)
        except (AssertionError, KeyError, ValueError) as error:
            print(f"C_{rank}: FAIL: {error}")
            raise SystemExit(1) from error
        print(
            f"C_{rank}: PASS: {report['basis_generators']} generators, "
            f"{report['antisymmetry_checks']} graded-skew checks, "
            f"{report['jacobi_checks']} super-Jacobi triples"
        )
