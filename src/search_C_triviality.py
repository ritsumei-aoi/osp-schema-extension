#!/usr/bin/env python3
"""Compare evaluated gamma outputs with the odd coboundary image."""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path

if __package__:
    from .evaluate_C import evaluate_schema1_gamma
else:
    from evaluate_C import evaluate_schema1_gamma


def _matrix_rank(rows, columns):
    matrix = [list(row) for row in rows]
    pivot_row = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(pivot_row, len(matrix))
             if matrix[row][column]),
            None,
        )
        if pivot is None:
            continue
        matrix[pivot_row], matrix[pivot] = matrix[pivot], matrix[pivot_row]
        scale = matrix[pivot_row][column]
        matrix[pivot_row] = [value / scale for value in matrix[pivot_row]]
        for row in range(len(matrix)):
            if row == pivot_row or not matrix[row][column]:
                continue
            factor = matrix[row][column]
            matrix[row] = [
                value - factor * pivot_value
                for value, pivot_value in zip(matrix[row], matrix[pivot_row])
            ]
        pivot_row += 1
        if pivot_row == len(matrix):
            break
    return pivot_row


def compare_rank(data_dir, n):
    root = Path(data_dir)
    with (root / f"C_{n}_structure.json").open(encoding="utf-8") as stream:
        structure = json.load(stream)
    with (root / f"C_{n}_gamma.json").open(encoding="utf-8") as stream:
        gamma = json.load(stream)
    with (root / f"C_{n}_evaluated.json").open(encoding="utf-8") as stream:
        evaluated_plus = json.load(stream)
    with (root / f"C_{n}_coboundary.json").open(encoding="utf-8") as stream:
        coboundary = json.load(stream)

    deformation = gamma["inhomogeneous_deformation"]
    parameters = [
        item["label"]
        for item in deformation["gb_matrix"]["parameters"]
    ]
    rows = []
    for entry in deformation["gamma_coefficients"]:
        if entry["Z"] != "K":
            continue
        values = {parameter: Fraction(0) for parameter in parameters}
        for term in entry["coefficients"]:
            values[term["parameter"]] += Fraction(term["coeff"])
        rows.append([values[parameter] for parameter in parameters])
    obstruction_rank = _matrix_rank(rows, len(parameters))

    coboundary_outputs = {
        entry["Z"]
        for entry in coboundary["coboundary"]["coboundary_coefficients"]
    }
    if "K" in coboundary_outputs:
        raise ValueError("Layer 4 unexpectedly contains the scalar output K")
    basis = set(structure["parity"])
    if not coboundary_outputs <= basis:
        raise ValueError("Layer 4 output is outside the Layer 1 basis")

    evaluated_entries = evaluated_plus["evaluated_structure_constants"]
    plus_obstructions = [
        entry for entry in evaluated_entries
        if entry["Z"] == "K" and entry["kappa_coeff"] != "0"
    ]
    zero = evaluate_schema1_gamma(structure, gamma, sign=0)
    zero_deformation = [
        entry for entry in zero["evaluated_structure_constants"]
        if entry["kappa_coeff"] != "0"
    ]
    parameter_count = 4 * n
    return {
        "rank": n,
        "parameter_count": parameter_count,
        "scalar_obstruction_matrix_rank": obstruction_rank,
        "kernel_dimension": parameter_count - obstruction_rank,
        "all_plus_scalar_obstructed": bool(plus_obstructions),
        "all_plus_scalar_obstructions": [
            {
                "X": entry["X"],
                "Y": entry["Y"],
                "Z": entry["Z"],
                "kappa_coeff": entry["kappa_coeff"],
            }
            for entry in plus_obstructions[:5]
        ],
        "zero_assignment_trivial": not zero_deformation,
        "coboundary_has_scalar_K": "K" in coboundary_outputs,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--ranks", nargs="+", type=int, default=[1, 2, 3])
    args = parser.parse_args(argv)
    failed = False
    for n in args.ranks:
        try:
            result = compare_rank(args.data_dir, n)
        except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
            failed = True
            print(f"FAIL C_{n}: {error}")
            continue
        print(
            f"C({n + 1}): scalar obstruction rank "
            f"{result['scalar_obstruction_matrix_rank']}/"
            f"{result['parameter_count']}; "
            f"all-plus scalar-obstructed="
            f"{result['all_plus_scalar_obstructed']}; "
            f"zero-assignment trivial={result['zero_assignment_trivial']}"
        )
        for entry in result["all_plus_scalar_obstructions"][:2]:
            print(
                f"  obstruction: ({entry['X']}, {entry['Y']}) -> K "
                f"with kappa coefficient {entry['kappa_coeff']}"
            )
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
