"""Evaluate C(n+1) gamma schemas at a concrete gb parameter assignment."""

from __future__ import annotations

import argparse
import json
from datetime import date
from fractions import Fraction
from pathlib import Path

from src.C_generators import ROOT, _coefficient


def evaluate_schema(n: int, assignment_value: int = 1) -> dict:
    if n < 1:
        raise ValueError("Bosonic rank n must be at least 1")
    if assignment_value not in (-1, 0, 1):
        raise ValueError("The uniform gb assignment value must be -1, 0, or +1")
    structure_path = ROOT / "data" / f"C_{n}_structure.json"
    gamma_path = ROOT / "data" / f"C_{n}_gamma.json"
    try:
        structure = json.loads(structure_path.read_text(encoding="utf-8"))
        gamma = json.loads(gamma_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read source schemas for rank {n}: {exc}") from exc

    if structure.get("algebra", {}).get("n") != n or gamma.get("algebra", {}).get("n") != n:
        raise ValueError(f"source schemas do not match bosonic rank n={n}")
    if gamma.get("source_schema") != structure_path.name:
        raise ValueError(f"{gamma_path.name} does not reference {structure_path.name}")
    parameters = gamma.get("gb_matrix", {}).get("parameters", [])
    expected_parameter_count = 4 * n
    if len(parameters) != expected_parameter_count:
        raise ValueError(
            f"{gamma_path.name} has {len(parameters)} parameters; expected {expected_parameter_count}"
        )
    parameter_labels = {parameter.get("label") for parameter in parameters}
    if None in parameter_labels or len(parameter_labels) != expected_parameter_count:
        raise ValueError(f"{gamma_path.name} contains missing or duplicate parameter labels")
    assignment = {label: assignment_value for label in sorted(parameter_labels)}

    values: dict[tuple[str, str, str], dict[str, Fraction]] = {}
    for entry in structure.get("structure_constants", []):
        key = (entry["X"], entry["Y"], entry["Z"])
        coefficients = values.setdefault(key, {"constant": Fraction(0), "kappa": Fraction(0)})
        coefficients["constant"] += Fraction(entry["coeff"])

    gamma_data = gamma.get("inhomogeneous_deformation", {}).get("gamma_coefficients", [])
    for entry in gamma_data:
        parameter = entry.get("parameter")
        if parameter not in assignment:
            raise ValueError(f"gamma term references unknown parameter {parameter!r}")
        key = (entry["X"], entry["Y"], entry["Z"])
        coefficients = values.setdefault(key, {"constant": Fraction(0), "kappa": Fraction(0)})
        coefficients["kappa"] += assignment[parameter] * Fraction(entry["coeff"])

    evaluated = []
    for (x, y, z), coefficients in sorted(values.items()):
        if not coefficients["constant"] and not coefficients["kappa"]:
            continue
        evaluated.append({
            "X": x,
            "Y": y,
            "Z": z,
            "coefficients": {
                "constant": _coefficient(coefficients["constant"]),
                "kappa": _coefficient(coefficients["kappa"]),
            },
            "sign_rule": "graded",
        })

    return {
        "schema_version": "5.0",
        "algebra": structure["algebra"],
        "source_structure_schema": structure_path.name,
        "source_gamma_schema": gamma_path.name,
        "evaluation_profile": {
            "name": {
                1: "all_positive",
                0: "all_zero",
                -1: "all_negative",
            }[assignment_value],
            "description": f"Every odd gb parameter is assigned {assignment_value:+d}",
            "parameter_value": assignment_value,
        },
        "gb_assignment": assignment,
        "coefficient_domain": "Q[kappa]/(kappa^2)",
        "evaluated_structure_constants": evaluated,
        "metadata": {
            "generated_by": "src/C_evaluate_structure.py",
            "generation_date": date.today().isoformat(),
            "references": [
                structure_path.name,
                gamma_path.name,
                "docs/json_schema_specification.md",
            ],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ranks", type=int, nargs="+", default=[1, 2, 3])
    parser.add_argument("--sign", type=int, choices=(-1, 1), default=1)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for n in args.ranks:
        evaluated = evaluate_schema(n, args.sign)
        path = args.output_dir / f"C_{n}_evaluated.json"
        path.write_text(json.dumps(evaluated, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Wrote {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}")


if __name__ == "__main__":
    main()
