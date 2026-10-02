#!/usr/bin/env python3
"""Compare evaluated deformation data with the odd-map coboundary layer."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

if __package__:
    from .C_generators import ROOT
else:
    from C_generators import ROOT

DATA_DIR = ROOT / "data"


def _matrix_rank(matrix: list[list[Fraction]]) -> int:
    if not matrix:
        return 0
    rows = [list(row) for row in matrix]
    height, width = len(rows), len(rows[0])
    pivot_row = 0
    for column in range(width):
        selected = next((row for row in range(pivot_row, height) if rows[row][column]), None)
        if selected is None:
            continue
        rows[pivot_row], rows[selected] = rows[selected], rows[pivot_row]
        divisor = rows[pivot_row][column]
        rows[pivot_row] = [value / divisor for value in rows[pivot_row]]
        for row in range(height):
            if row == pivot_row or not rows[row][column]:
                continue
            factor = rows[row][column]
            rows[row] = [
                value - factor * pivot
                for value, pivot in zip(rows[row], rows[pivot_row])
            ]
        pivot_row += 1
        if pivot_row == height:
            break
    return pivot_row


def analyze_rank(n: int, data_dir: Path = DATA_DIR) -> dict[str, object]:
    paths = {
        "gamma": data_dir / f"C_{n}_gamma.json",
        "evaluated": data_dir / f"C_{n}_evaluated.json",
        "coboundary": data_dir / f"C_{n}_coboundary.json",
        "structure": data_dir / f"C_{n}_structure.json",
    }
    loaded = {}
    for name, path in paths.items():
        with path.open(encoding="utf-8") as stream:
            loaded[name] = json.load(stream)
    gamma = loaded["gamma"]
    evaluated = loaded["evaluated"]
    coboundary = loaded["coboundary"]
    structure = loaded["structure"]

    basis = set(structure["basis"]["even"] + structure["basis"]["odd"])
    if any(data["algebra"] != structure["algebra"] for data in loaded.values()):
        raise ValueError(f"Schema layers disagree on C(n+1) rank {n}")
    if any(
        target["target"] not in basis
        for mappings in coboundary["odd_linear_map"]["coefficients"].values()
        for target in mappings
    ):
        raise ValueError("Coboundary map contains targets outside the Schema 1 basis")
    if any(entry["Z"] == "K" for entry in coboundary["coboundary_definition"]["coboundary_coefficients"]):
        raise ValueError("Coboundary layer must target g, not the excluded identity K")

    parameters = [
        parameter
        for row in gamma["gb_matrix"]["parameters"]
        for parameter in row
    ]
    central_entries = [
        entry for entry in gamma["inhomogeneous_deformation"]["gamma_coefficients"]
        if entry["Z"] == "K"
    ]
    obstruction_matrix = [
        [
            next(
                (
                    Fraction(term["coeff"])
                    for term in entry["coefficients"]
                    if term["parameter"] == parameter
                ),
                Fraction(0),
            )
            for parameter in parameters
        ]
        for entry in central_entries
    ]
    obstruction_rank = _matrix_rank(obstruction_matrix)

    assignment = evaluated["gb_assignment"]["values"]
    central_evaluated = [
        entry for entry in evaluated["evaluated_structure_constants"]
        if entry["kappa_order"] == 1 and entry["Z"] == "K" and Fraction(entry["coeff"])
    ]
    if assignment and set(assignment.values()) == {1}:
        example = next(
            (
                entry for entry in central_evaluated
                if entry["X"] == "H_1" and entry["Y"] == "E_eps1_del1_pm"
            ),
            central_evaluated[0] if central_evaluated else None,
        )
    else:
        example = None

    triviality_condition = (
        "all gb parameters are zero"
        if obstruction_rank == len(parameters)
        else "the central-obstruction matrix times the gb vector is zero"
    )
    return {
        "n": n,
        "parameter_count": len(parameters),
        "central_obstruction_rows": len(central_entries),
        "central_obstruction_rank": obstruction_rank,
        "all_plus_has_central_mismatch": bool(central_evaluated),
        "all_plus_example": example,
        "necessary_condition": triviality_condition,
        "sufficient_at_zero": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    args = parser.parse_args()
    for n in (1, 2, 3):
        report = analyze_rank(n, args.data_dir)
        print(
            f"C_{n}: central obstruction rank {report['central_obstruction_rank']}/"
            f"{report['parameter_count']}; "
            f"all-plus central mismatch={report['all_plus_has_central_mismatch']}; "
            f"condition: {report['necessary_condition']}"
        )
        if report["all_plus_example"]:
            entry = report["all_plus_example"]
            print(
                f"  example: [{entry['X']}, {entry['Y']}] -> "
                f"{entry['coeff']} κ K; no corresponding K target in Layer 4"
            )


if __name__ == "__main__":
    main()
