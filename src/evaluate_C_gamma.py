#!/usr/bin/env python3
"""Substitute the uniform +1 gb profile into C(n+1) gamma data."""

from __future__ import annotations

import argparse
import json
from datetime import date
from fractions import Fraction
from pathlib import Path


def _fraction_string(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def evaluate_schema(structure: dict, gamma: dict) -> dict:
    n = structure["algebra"]["n"]
    if gamma["algebra"]["n"] != n:
        raise ValueError("Schema 1 and Schema 2 ranks do not match")
    if structure["algebra"]["family"] != "C" or gamma["algebra"]["family"] != "C":
        raise ValueError("only C-family structure and gamma schemas are supported")
    matrix = gamma["gb_matrix"]
    expected_shape = [2, 2 * n]
    if matrix["shape"] != expected_shape:
        raise ValueError(f"gb matrix shape {matrix['shape']} does not match {expected_shape}")
    parameters = [parameter for row in matrix["entries"] for parameter in row]
    if len(parameters) != 4 * n or len(set(parameters)) != 4 * n:
        raise ValueError("gb matrix must contain 4n distinct parameter labels")
    assignment = {parameter: 1 for parameter in parameters}

    evaluated: dict[tuple[str, str, str], dict[str, Fraction]] = {}
    for row in structure["structure_constants"]:
        key = (row["X"], row["Y"], row["Z"])
        coefficients = evaluated.setdefault(
            key, {"base": Fraction(), "gamma": Fraction()}
        )
        coefficients["base"] += Fraction(row["coeff"])
    for row in gamma["inhomogeneous_deformation"]["gamma_coefficients"]:
        key = (row["X"], row["Y"], row["Z"])
        coefficients = evaluated.setdefault(
            key, {"base": Fraction(), "gamma": Fraction()}
        )
        for term in row["terms"]:
            parameter = term["parameter"]
            if parameter not in assignment:
                raise ValueError(f"gamma coefficient references unknown parameter {parameter}")
            coefficients["gamma"] += Fraction(term["coeff"]) * assignment[parameter]

    basis = set(structure["basis"]["even"] + structure["basis"]["odd"])
    records = []
    for (x, y, z), coefficients in sorted(evaluated.items()):
        if x not in basis or y not in basis or z not in basis | {"K"}:
            raise ValueError(f"evaluated bracket references unknown generator: {(x, y, z)}")
        base, deformation = coefficients["base"], coefficients["gamma"]
        if base or deformation:
            records.append({
                "X": x,
                "Y": y,
                "Z": z,
                "base_coeff": _fraction_string(base),
                "evaluated_gamma_coeff": _fraction_string(deformation),
            })

    return {
        "schema_version": "5.0",
        "algebra": structure["algebra"],
        "evaluation": {
            "profile": "uniform_plus_one",
            "central_symbol": "kappa",
            "parameter_assignment": assignment,
        },
        "basis": structure["basis"],
        "parity": structure["parity"],
        "central_elements": structure["central_elements"],
        "evaluated_structure_constants": records,
        "metadata": {
            "generated_by": "evaluate_C_gamma.py",
            "generation_date": date.today().isoformat(),
            "source_structure": f"C_{n}_structure.json",
            "source_gamma": f"C_{n}_gamma.json",
        },
    }


def evaluate_files(data_dir: Path, ranks: tuple[int, ...] = (1, 2, 3)) -> list[Path]:
    outputs = []
    for n in ranks:
        structure_path = data_dir / f"C_{n}_structure.json"
        gamma_path = data_dir / f"C_{n}_gamma.json"
        structure = json.loads(structure_path.read_text(encoding="utf-8"))
        gamma = json.loads(gamma_path.read_text(encoding="utf-8"))
        result = evaluate_schema(structure, gamma)
        output_path = data_dir / f"C_{n}_evaluated.json"
        output_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        outputs.append(output_path)
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data",
    )
    parser.add_argument("--ranks", type=int, nargs="+", default=(1, 2, 3))
    args = parser.parse_args()
    for path in evaluate_files(args.data_dir, tuple(args.ranks)):
        print(path)


if __name__ == "__main__":
    main()
