#!/usr/bin/env python3
"""Substitute a concrete gb assignment into C-family Schema 2 data."""

from __future__ import annotations

import argparse
import json
from datetime import date
from fractions import Fraction
from pathlib import Path

if __package__:
    from .C_gamma_generator import _parse_gamma_expression
else:
    from C_gamma_generator import _parse_gamma_expression


def evaluate_gamma_schema(
    structure: dict,
    gamma: dict,
    assignment_name: str = "all_plus",
    assignment_value: int = 1,
    generation_date: str | None = None,
) -> dict:
    rank = structure["algebra"]["n"]
    if gamma["algebra"]["family"] != "C" or gamma["algebra"]["n"] != rank:
        raise ValueError("Schema 2 algebra does not match the Schema 1 source")
    if gamma["source_schema"] != f"C_{rank}_structure.json":
        raise ValueError("Schema 2 references the wrong Schema 1 file")

    parameters = [
        parameter
        for row in gamma["gb_matrix"]["entries"]
        for parameter in row
    ]
    expected_parameter_count = 4 * rank
    if (
        gamma["gb_matrix"]["shape"] != [2, 2 * rank]
        or len(parameters) != expected_parameter_count
        or len(set(parameters)) != expected_parameter_count
    ):
        raise ValueError("Schema 2 gb_matrix has an invalid shape or parameter set")
    assignment = {parameter: assignment_value for parameter in parameters}

    base: dict[tuple[str, str, str], Fraction] = {}
    for entry in structure["structure_constants"]:
        key = (entry["X"], entry["Y"], entry["Z"])
        if key in base:
            raise ValueError(f"Duplicate Schema 1 structure constant: {key}")
        base[key] = Fraction(entry["coeff"])

    deformation: dict[tuple[str, str, str], Fraction] = {}
    for entry in gamma["inhomogeneous_deformation"]["gamma_coefficients"]:
        key = (entry["X"], entry["Y"], entry["Z"])
        evaluated = sum(
            (
                coefficient * assignment[parameter]
                for parameter, coefficient
                in _parse_gamma_expression(entry["coeff"]).items()
            ),
            Fraction(),
        )
        deformation[key] = deformation.get(key, Fraction()) + evaluated

    keys = sorted(set(base) | set(deformation))
    records = []
    for x, y, z in keys:
        base_coefficient = base.get((x, y, z), Fraction())
        gamma_coefficient = deformation.get((x, y, z), Fraction())
        if base_coefficient or gamma_coefficient:
            records.append({
                "X": x,
                "Y": y,
                "Z": z,
                "base_coeff": str(base_coefficient),
                "kappa_coeff": str(gamma_coefficient),
                "sign_rule": "graded",
            })

    labels = set(structure["basis"]["even"] + structure["basis"]["odd"])
    labels.add("K")
    if any(
        not {record["X"], record["Y"], record["Z"]} <= labels
        for record in records
    ):
        raise ValueError("Evaluated records reference labels outside the schema")

    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": rank,
            "cartan_type": f"C({rank + 1})",
        },
        "source_schema": f"C_{rank}_structure.json",
        "source_gamma_schema": f"C_{rank}_gamma.json",
        "gb_assignment": {
            "name": assignment_name,
            "description": f"All {expected_parameter_count} gb parameters set to {assignment_value:+d}",
            "values": assignment,
        },
        "evaluated_structure": {
            "coefficient_convention": "base_coeff + kappa * kappa_coeff",
            "structure_constants": records,
        },
        "metadata": {
            "generated_by": "src/evaluate_C_gamma.py",
            "generation_date": generation_date or date.today().isoformat(),
        },
    }


def validate_evaluated_schema(
    evaluated: dict, structure: dict, gamma: dict
) -> None:
    rank = structure["algebra"]["n"]
    expected_assignment = {
        parameter
        for row in gamma["gb_matrix"]["entries"]
        for parameter in row
    }
    assignment = evaluated["gb_assignment"]["values"]
    if set(assignment) != expected_assignment:
        raise ValueError("Evaluated assignment does not cover exactly the gb matrix")
    if any(value != 1 for value in assignment.values()):
        raise ValueError("The all-plus representative assignment must be +1")
    if evaluated["algebra"]["n"] != rank:
        raise ValueError("Evaluated schema rank does not match its source")

    expected = evaluate_gamma_schema(
        structure,
        gamma,
        assignment_name=evaluated["gb_assignment"]["name"],
        assignment_value=1,
        generation_date=evaluated["metadata"]["generation_date"],
    )
    if evaluated != expected:
        raise ValueError("Evaluated data does not match Schema 1 + substituted Schema 2")


def write_evaluated_schemas(data_dir: Path, ranks: list[int]) -> list[Path]:
    outputs = []
    for rank in ranks:
        with (data_dir / f"C_{rank}_structure.json").open(encoding="utf-8") as stream:
            structure = json.load(stream)
        with (data_dir / f"C_{rank}_gamma.json").open(encoding="utf-8") as stream:
            gamma = json.load(stream)
        evaluated = evaluate_gamma_schema(structure, gamma)
        validate_evaluated_schema(evaluated, structure, gamma)
        output = data_dir / f"C_{rank}_evaluated.json"
        output.write_text(json.dumps(evaluated, indent=2) + "\n", encoding="utf-8")
        outputs.append(output)
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--ranks", type=int, nargs="+", default=[1, 2, 3])
    args = parser.parse_args()
    for path in write_evaluated_schemas(args.data_dir, args.ranks):
        print(path)


if __name__ == "__main__":
    main()
