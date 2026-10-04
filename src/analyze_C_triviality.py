#!/usr/bin/env python3
"""Compare evaluated C(n+1) deformations with their coboundary spaces."""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path


def _matrix_rank(rows: list[list[Fraction]]) -> int:
    if not rows:
        return 0
    matrix = [row[:] for row in rows]
    row_count = len(matrix)
    column_count = len(matrix[0])
    rank = 0
    for column in range(column_count):
        pivot = next(
            (row for row in range(rank, row_count) if matrix[row][column]),
            None,
        )
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        divisor = matrix[rank][column]
        matrix[rank] = [value / divisor for value in matrix[rank]]
        for row in range(row_count):
            if row == rank or not matrix[row][column]:
                continue
            factor = matrix[row][column]
            matrix[row] = [
                left - factor * right
                for left, right in zip(matrix[row], matrix[rank])
            ]
        rank += 1
        if rank == row_count:
            break
    return rank


def analyze_rank(data_dir: Path, n: int) -> list[str]:
    gamma = json.loads(
        (data_dir / f"C_{n}_gamma.json").read_text(encoding="utf-8")
    )
    plus = json.loads(
        (data_dir / f"C_{n}_evaluated.json").read_text(encoding="utf-8")
    )
    zero = json.loads(
        (data_dir / f"C_{n}_evaluated_zero.json").read_text(encoding="utf-8")
    )
    coboundary = json.loads(
        (data_dir / f"C_{n}_coboundary.json").read_text(encoding="utf-8")
    )

    parameters = [
        parameter
        for row in gamma["gb_matrix"]["entries"]
        for parameter in row
    ]
    central_rows: dict[tuple[str, str], dict[str, Fraction]] = {}
    for record in gamma["inhomogeneous_deformation"]["gamma_coefficients"]:
        if record["Z"] != "K":
            continue
        row = central_rows.setdefault((record["X"], record["Y"]), {})
        for term in record["coefficients"]:
            parameter = term["parameter"]
            row[parameter] = row.get(parameter, Fraction(0)) + Fraction(term["coeff"])
    matrix = [
        [row.get(parameter, Fraction(0)) for parameter in parameters]
        for _, row in sorted(central_rows.items())
    ]
    rank = _matrix_rank(matrix)

    plus_central = [
        record
        for record in plus["evaluated_structure_constants"]
        if record["Z"] == "K" and Fraction(record["kappa_coeff"])
    ]
    if not plus_central:
        raise ValueError(f"C_{n}: all-plus data has no central obstruction")
    coboundary_central = [
        record
        for record in coboundary["coboundary_coefficients"]
        if record["Z"] == "K"
    ]
    if coboundary_central:
        raise ValueError(f"C_{n}: coboundary unexpectedly contains K outputs")

    if any(Fraction(record["kappa_coeff"]) for record in zero["evaluated_structure_constants"]):
        raise ValueError(f"C_{n}: all-zero assignment has nonzero gamma")
    if plus["gb_assignment"]["values"] != {parameter: 1 for parameter in parameters}:
        raise ValueError(f"C_{n}: evaluated all-plus assignment is incomplete")
    if zero["gb_assignment"]["values"] != {parameter: 0 for parameter in parameters}:
        raise ValueError(f"C_{n}: evaluated all-zero assignment is incomplete")
    if rank != len(parameters):
        raise ValueError(
            f"C_{n}: central obstruction rank {rank} is below {len(parameters)}"
        )

    first = plus_central[0]
    witness_text = (
        f"({first['X']}, {first['Y']}) -> K: "
        f"kappa_coeff={first['kappa_coeff']}"
    )
    return [
        f"C_{n}: central obstruction matrix rank {rank}/{len(parameters)}",
        f"C_{n}: all-plus is non-trivial; {witness_text}, while coboundaries have no K component",
        f"C_{n}: all-zero is trivial; evaluated gamma is zero and f=0 gives delta_f=0",
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    args = parser.parse_args()
    try:
        for n in (1, 2, 3):
            for line in analyze_rank(args.data_dir, n):
                print(line)
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        print(f"FAIL: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
