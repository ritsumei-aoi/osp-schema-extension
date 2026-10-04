#!/usr/bin/env python3
"""Evaluate the C(n+1) gamma layer at the all-plus gb assignment."""

from __future__ import annotations

import argparse
import json
from datetime import date
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


def build_evaluated_schema(
    rank: int,
    structure_schema: dict[str, object],
    gamma_schema: dict[str, object],
) -> dict[str, object]:
    if rank < 1:
        raise ValueError("The bosonic rank n must be at least 1")
    for schema, label in ((structure_schema, "structure"), (gamma_schema, "gamma")):
        if schema["algebra"]["family"] != "C" or schema["algebra"]["n"] != rank:
            raise ValueError(f"{label} schema does not match C rank {rank}")
    if gamma_schema["source_schema"] != f"C_{rank}_structure.json":
        raise ValueError(f"Gamma schema does not reference the C_{rank} structure file")

    basis = set(structure_schema["parity"])
    parameters = [
        parameter
        for row in gamma_schema["gb_matrix"]["entries"].values()
        for parameter in row.values()
    ]
    if len(parameters) != 4 * rank or len(set(parameters)) != 4 * rank:
        raise ValueError(f"Gamma schema must define 4n distinct parameters for rank {rank}")

    evaluated: dict[tuple[str, str, str], dict[str, Fraction]] = {}
    for entry in structure_schema["structure_constants"]:
        if any(entry[key] not in basis for key in ("X", "Y", "Z")):
            raise ValueError(f"Schema 1 bracket references an unknown generator: {entry}")
        key = entry["X"], entry["Y"], entry["Z"]
        values = evaluated.setdefault(key, {"coeff": Fraction(0), "kappa_coeff": Fraction(0)})
        values["coeff"] += Fraction(entry["coeff"])

    assignment = {parameter: 1 for parameter in parameters}
    for entry in gamma_schema["gamma_structure"]:
        if entry["gb"] not in assignment:
            raise ValueError(f"Gamma parameter has no all-plus assignment: {entry['gb']}")
        if entry["X"] not in basis or entry["Y"] not in basis:
            raise ValueError(f"Gamma bracket input is not in Schema 1 basis: {entry}")
        if entry["Z"] not in basis | {"K"}:
            raise ValueError(f"Gamma bracket output is not in Schema 1 basis or K: {entry}")
        key = entry["X"], entry["Y"], entry["Z"]
        values = evaluated.setdefault(key, {"coeff": Fraction(0), "kappa_coeff": Fraction(0)})
        values["kappa_coeff"] += Fraction(entry["coeff"]) * assignment[entry["gb"]]

    constants = [
        {
            "X": left,
            "Y": right,
            "Z": output,
            "coeff": str(values["coeff"]),
            "kappa_coeff": str(values["kappa_coeff"]),
            "sign_rule": "graded",
        }
        for (left, right, output), values in sorted(evaluated.items())
        if values["coeff"] or values["kappa_coeff"]
    ]
    return {
        "schema_version": "5.0",
        "schema_layer": 3,
        "algebra": structure_schema["algebra"],
        "source_files": {
            "schema_1": f"C_{rank}_structure.json",
            "schema_2": f"C_{rank}_gamma.json",
        },
        "gb_assignment": {
            "profile": "all_plus",
            "parameter_parity": gamma_schema["gb_matrix"]["parameter_parity"],
            "values": assignment,
        },
        "central_elements": structure_schema["central_elements"],
        "structure_constants": constants,
        "metadata": {
            "generated_by": "src/evaluate_C.py",
            "generation_date": date.today().isoformat(),
            "references": [
                "docs/json_schema_specification.md",
                "docs/math/C_inhomogeneous_definition.md",
            ],
        },
    }


def evaluate_rank(rank: int, data_dir: Path = DATA_DIR) -> Path:
    files = {
        "structure": data_dir / f"C_{rank}_structure.json",
        "gamma": data_dir / f"C_{rank}_gamma.json",
    }
    schemas = {}
    for label, path in files.items():
        with path.open(encoding="utf-8") as stream:
            schemas[label] = json.load(stream)
    evaluated = build_evaluated_schema(rank, schemas["structure"], schemas["gamma"])
    output_path = data_dir / f"C_{rank}_evaluated.json"
    output_path.write_text(
        json.dumps(evaluated, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ranks", type=int, nargs="+", default=[1, 2, 3])
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    arguments = parser.parse_args()
    for rank in arguments.ranks:
        print(evaluate_rank(rank, arguments.data_dir))


if __name__ == "__main__":
    main()
