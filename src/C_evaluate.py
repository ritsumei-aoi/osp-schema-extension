#!/usr/bin/env python3
"""Evaluate a C(n+1) Schema 2 gamma file at a concrete gb assignment."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import date
from fractions import Fraction
from pathlib import Path

if __package__:
    from .C_generators import ROOT
else:
    from C_generators import ROOT

DATA_DIR = ROOT / "data"


def evaluate_schema(n: int, structure_path: Path | None = None, gamma_path: Path | None = None) -> dict[str, object]:
    if n < 1:
        raise ValueError("n must be at least 1")
    structure_file = structure_path or DATA_DIR / f"C_{n}_structure.json"
    gamma_file = gamma_path or DATA_DIR / f"C_{n}_gamma.json"
    with structure_file.open(encoding="utf-8") as stream:
        structure = json.load(stream)
    with gamma_file.open(encoding="utf-8") as stream:
        gamma = json.load(stream)

    if structure["algebra"]["family"] != "C" or structure["algebra"]["n"] != n:
        raise ValueError(f"{structure_file} does not match C-family rank {n}")
    if gamma["algebra"] != structure["algebra"]:
        raise ValueError(f"{gamma_file} algebra descriptor does not match {structure_file}")
    if gamma["source_schema"] != structure_file.name:
        raise ValueError(f"{gamma_file} does not reference {structure_file.name}")
    if gamma["gb_matrix"]["shape"] != [2, 2 * n]:
        raise ValueError(f"{gamma_file} does not contain a 2 x {2 * n} gb matrix")

    parameters = [
        parameter
        for row in gamma["gb_matrix"]["parameters"]
        for parameter in row
    ]
    assignment = {parameter: 1 for parameter in parameters}
    if len(assignment) != 4 * n:
        raise ValueError(f"{gamma_file} does not provide all {4 * n} distinct gb parameters")

    evaluated: defaultdict[tuple[str, str, str, int], Fraction] = defaultdict(Fraction)
    for entry in structure["structure_constants"]:
        key = (entry["X"], entry["Y"], entry["Z"], 0)
        evaluated[key] += Fraction(entry["coeff"])

    referenced_parameters: set[str] = set()
    for entry in gamma["inhomogeneous_deformation"]["gamma_coefficients"]:
        for term in entry["coefficients"]:
            parameter = term["parameter"]
            if parameter not in assignment:
                raise ValueError(f"Gamma term references unknown gb parameter {parameter}")
            referenced_parameters.add(parameter)
            key = (entry["X"], entry["Y"], entry["Z"], 1)
            evaluated[key] += Fraction(term["coeff"]) * assignment[parameter]
    if referenced_parameters - assignment.keys():
        raise ValueError("Not all referenced gb parameters have assigned values")

    result = [
        {
            "X": x,
            "Y": y,
            "Z": z,
            "coeff": str(coeff),
            "kappa_order": kappa_order,
        }
        for (x, y, z, kappa_order), coeff in sorted(evaluated.items())
        if coeff
    ]
    return {
        "schema_version": "5.0",
        "algebra": structure["algebra"],
        "source_schema": structure_file.name,
        "source_gamma": gamma_file.name,
        "gb_assignment": {
            "profile": "all_plus_one",
            "values": assignment,
            "rationale": "Uniform nonzero profile for a reproducible representative evaluation",
        },
        "evaluated_structure_constants": result,
        "metadata": {
            "generated_by": "src/C_evaluate.py",
            "generation_date": date.today().isoformat(),
            "references": ["docs/json_schema_specification.md"],
        },
    }


def generate(n: int, output_dir: Path = DATA_DIR) -> Path:
    schema = evaluate_schema(n)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"C_{n}_evaluated.json"
    path.write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, nargs="+", default=[1, 2, 3])
    parser.add_argument("--output-dir", type=Path, default=DATA_DIR)
    args = parser.parse_args()
    for rank in args.n:
        print(generate(rank, args.output_dir))


if __name__ == "__main__":
    main()
