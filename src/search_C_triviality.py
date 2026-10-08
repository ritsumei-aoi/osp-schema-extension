#!/usr/bin/env python3
"""Compare evaluated gamma data with the odd-map coboundary image."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path


def analyze_rank(n: int, data_dir: Path) -> dict:
    gamma = json.loads(
        (data_dir / f"C_{n}_gamma.json").read_text(encoding="utf-8")
    )
    evaluated = json.loads(
        (data_dir / f"C_{n}_evaluated.json").read_text(encoding="utf-8")
    )
    coboundary = json.loads(
        (data_dir / f"C_{n}_coboundary.json").read_text(encoding="utf-8")
    )
    parameters = {
        parameter
        for row in gamma["gb_matrix"]["entries"]
        for parameter in row
    }
    coboundary_targets = {
        row["Z"] for row in coboundary["coboundary"]["coefficients"]
    }
    if "K" in coboundary_targets:
        raise ValueError("coboundary output unexpectedly includes central identity K")

    witnesses: dict[str, dict] = {}
    for row in gamma["inhomogeneous_deformation"]["gamma_coefficients"]:
        if row["Z"] != "K" or len(row["terms"]) != 1:
            continue
        term = row["terms"][0]
        parameter = term["parameter"]
        if Fraction(term["coeff"]) and parameter not in witnesses:
            witnesses[parameter] = {
                "X": row["X"],
                "Y": row["Y"],
                "Z": "K",
                "gamma_coeff": term["coeff"],
            }
    missing = parameters - set(witnesses)
    if missing:
        raise ValueError(f"gb parameters lack individual K obstructions: {sorted(missing)}")

    evaluated_k = [
        row for row in evaluated["evaluated_structure_constants"]
        if row["Z"] == "K" and Fraction(row["evaluated_gamma_coeff"])
    ]
    if not evaluated_k:
        raise ValueError("uniform +1 assignment has no nonzero central obstruction")
    gamma_rows = gamma["inhomogeneous_deformation"]["gamma_coefficients"]
    zero_specialization = all(
        row["terms"]
        and all(term["parameter"] in parameters for term in row["terms"])
        for row in gamma_rows
    )
    if not zero_specialization:
        raise ValueError("zero gb assignment unexpectedly has a nonzero gamma coefficient")

    return {
        "rank": n,
        "parameter_count": len(parameters),
        "individual_K_obstructions": len(witnesses),
        "uniform_plus_one_nontrivial": True,
        "uniform_plus_one_nonzero_K_rows": len(evaluated_k),
        "zero_assignment_trivial": zero_specialization,
        "triviality_conditions": [
            {
                "parameter": parameter,
                **witnesses[parameter],
                "necessary_condition": f"{parameter} = 0",
            }
            for parameter in sorted(parameters)
        ],
        "sample_uniform_plus_one_obstructions": [
            {
                "X": row["X"],
                "Y": row["Y"],
                "Z": row["Z"],
                "evaluated_gamma_coeff": row["evaluated_gamma_coeff"],
            }
            for row in evaluated_k[:4]
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data",
    )
    parser.add_argument("--ranks", type=int, nargs="+", default=(1, 2, 3))
    args = parser.parse_args()
    report = [analyze_rank(n, args.data_dir) for n in args.ranks]
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
