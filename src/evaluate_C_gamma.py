#!/usr/bin/env python3
"""Evaluate C(n+1) gamma coefficients at an explicit numeric gb assignment."""

from __future__ import annotations

import argparse
import json
from datetime import date
from fractions import Fraction
from pathlib import Path


def _fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def evaluate_schema1_schema2(
    structure: dict, gamma: dict, profile: str = "all_plus"
) -> dict:
    if structure["algebra"] != gamma["algebra"]:
        raise ValueError("Schema 1 and Schema 2 algebra fields do not match")
    if gamma["source_schema1"] != f"C_{structure['algebra']['n']}_structure.json":
        raise ValueError("Schema 2 source_schema1 does not match the loaded rank")

    matrix = gamma["gb_matrix"]
    parameter_labels = [
        parameter for row in matrix["entries"] for parameter in row
    ]
    if len(parameter_labels) != len(set(parameter_labels)):
        raise ValueError("gb_matrix contains duplicate parameter names")
    if profile == "all_plus":
        assignment = {parameter: 1 for parameter in parameter_labels}
    elif profile == "all_zero":
        assignment = {parameter: 0 for parameter in parameter_labels}
    else:
        raise ValueError(f"Unsupported gb assignment profile: {profile}")

    evaluated: dict[tuple[str, str, str], dict[str, Fraction]] = {}

    def get_component(x: str, y: str, z: str) -> dict[str, Fraction]:
        return evaluated.setdefault(
            (x, y, z), {"coeff": Fraction(0), "kappa_coeff": Fraction(0)}
        )

    for record in structure["structure_constants"]:
        component = get_component(record["X"], record["Y"], record["Z"])
        component["coeff"] += Fraction(record["coeff"])

    known = set(assignment)
    for record in gamma["inhomogeneous_deformation"]["gamma_coefficients"]:
        component = get_component(record["X"], record["Y"], record["Z"])
        for term in record["coefficients"]:
            parameter = term["parameter"]
            if parameter not in known:
                raise ValueError(f"Gamma coefficient references unknown gb: {parameter}")
            component["kappa_coeff"] += (
                Fraction(term["coeff"]) * assignment[parameter]
            )

    records = []
    for (x, y, z), components in sorted(evaluated.items()):
        if not components["coeff"] and not components["kappa_coeff"]:
            continue
        records.append(
            {
                "X": x,
                "Y": y,
                "Z": z,
                "coeff": _fraction_text(components["coeff"]),
                "kappa_coeff": _fraction_text(components["kappa_coeff"]),
                "sign_rule": "graded",
            }
        )

    n = structure["algebra"]["n"]
    return {
        "schema_version": "5.0",
        "algebra": structure["algebra"],
        "source_schema1": f"C_{n}_structure.json",
        "source_schema2": f"C_{n}_gamma.json",
        "gb_assignment": {
            "profile": profile,
            "values": assignment,
        },
        "evaluated_structure_constants": records,
        "metadata": {
            "generated_by": "src/evaluate_C_gamma.py",
            "generation_date": date.today().isoformat(),
            "formula": "[X,Y] = sum(coeff * Z) + kappa * sum(kappa_coeff * Z)",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, nargs="+", default=[1, 2, 3])
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument(
        "--profile",
        choices=("all_plus", "all_zero"),
        default="all_plus",
    )
    args = parser.parse_args()

    for n in args.n:
        structure_path = args.data_dir / f"C_{n}_structure.json"
        gamma_path = args.data_dir / f"C_{n}_gamma.json"
        structure = json.loads(structure_path.read_text(encoding="utf-8"))
        gamma = json.loads(gamma_path.read_text(encoding="utf-8"))
        result = evaluate_schema1_schema2(structure, gamma, args.profile)
        suffix = "" if args.profile == "all_plus" else "_zero"
        output_path = args.data_dir / f"C_{n}_evaluated{suffix}.json"
        output_path.write_text(
            json.dumps(result, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
