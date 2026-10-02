#!/usr/bin/env python3
"""Evaluate a C(n+1) gamma schema at a fixed gb assignment."""

from __future__ import annotations

import json
from datetime import date
from fractions import Fraction
from pathlib import Path


def _format(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def evaluate_schema(gamma: dict, structure: dict, assignment: dict[str, int]) -> dict:
    n = gamma["algebra"]["n"]
    expected_parameters = set(gamma["gb_matrix"]["parameters"])
    if set(assignment) != expected_parameters:
        missing = sorted(expected_parameters - set(assignment))
        extra = sorted(set(assignment) - expected_parameters)
        raise ValueError(f"Assignment mismatch; missing={missing}, extra={extra}")
    if any(value not in (-1, 1) for value in assignment.values()):
        raise ValueError("This evaluator accepts only concrete signs -1 or +1")
    if structure["algebra"]["n"] != n:
        raise ValueError("Schema 1 and Schema 2 ranks do not match")

    evaluated: dict[tuple[str, str, str], dict[str, Fraction]] = {}
    for entry in structure["structure_constants"]:
        key = (entry["X"], entry["Y"], entry["Z"])
        evaluated.setdefault(key, {})["base"] = Fraction(entry["coeff"])
    for entry in gamma["inhomogeneous_deformation"]["gamma_coefficients"]:
        key = (entry["X"], entry["Y"], entry["Z"])
        values = evaluated.setdefault(key, {})
        values["kappa"] = values.get("kappa", Fraction()) + (
            Fraction(entry["coeff"]) * assignment[entry["parameter"]]
        )

    constants = [
        {
            "X": x,
            "Y": y,
            "Z": z,
            "base_coeff": _format(values.get("base", Fraction())),
            "kappa_coeff": _format(values.get("kappa", Fraction())),
            "sign_rule": "graded",
        }
        for (x, y, z), values in sorted(evaluated.items())
        if values.get("base", Fraction()) or values.get("kappa", Fraction())
    ]
    return {
        "schema_version": "5.0",
        "algebra": gamma["algebra"],
        "source_files": {
            "schema1": gamma["algebra"]["schema1_file"],
            "schema2": f"C_{n}_gamma.json",
        },
        "gb_assignment": {
            "profile": "all_plus_one",
            "description": "Every gb parameter is evaluated at +1",
            "values": {name: assignment[name] for name in gamma["gb_matrix"]["parameters"]},
        },
        "evaluation_convention": (
            "[X,Y]_evaluated = [X,Y]_0 + kappa * "
            "sum(parameter_value * gamma_parameter(X,Y))"
        ),
        "structure_constants": constants,
        "metadata": {
            "generated_by": "src/C_evaluate.py",
            "generation_date": date.today().isoformat(),
            "references": ["Schema 1 and Schema 2 C(n+1) data"],
        },
    }


def evaluate_files(
    data_dir: Path | str = "data",
    ranks: tuple[int, ...] = (1, 2, 3),
) -> None:
    data_dir = Path(data_dir)
    for n in ranks:
        gamma_path = data_dir / f"C_{n}_gamma.json"
        structure_path = data_dir / f"C_{n}_structure.json"
        gamma = json.loads(gamma_path.read_text(encoding="utf-8"))
        structure = json.loads(structure_path.read_text(encoding="utf-8"))
        assignment = {name: 1 for name in gamma["gb_matrix"]["parameters"]}
        result = evaluate_schema(gamma, structure, assignment)
        output_path = data_dir / f"C_{n}_evaluated.json"
        output_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    evaluate_files()
