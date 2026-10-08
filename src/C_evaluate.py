"""Evaluate the symbolic C(n+1) deformation at a fixed gb assignment."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import sympy as sp


def evaluate_gamma(gamma_data: dict, assignment: dict[str, int]) -> dict:
    deformation = gamma_data["inhomogeneous_deformation"]
    parameters = {
        parameter
        for row in deformation["gb_matrix"]["values"]
        for parameter in row
    }
    if set(assignment) != parameters:
        missing = sorted(parameters - set(assignment))
        extra = sorted(set(assignment) - parameters)
        raise ValueError(f"gb assignment mismatch; missing={missing}, extra={extra}")
    if any(value not in (-1, 1) for value in assignment.values()):
        raise ValueError("Each evaluated gb parameter must be +1 or -1")

    substitutions = {
        sp.Symbol(parameter): sp.Integer(value)
        for parameter, value in assignment.items()
    }
    evaluated = []
    for entry in deformation["gamma_coefficients"]:
        value = sp.simplify(sp.sympify(entry["coeff"]).subs(substitutions))
        if value:
            evaluated.append({**entry, "coeff": str(value)})

    result = copy.deepcopy(gamma_data)
    result["evaluated_deformation"] = {
        "input_file": f"C_{gamma_data['algebra']['n']}_gamma.json",
        "gb_assignment": assignment,
        "assignment_profile": "all parameters set to +1",
        "evaluated_coefficients": evaluated,
    }
    return result


def write_evaluated(rank: int, data_dir: Path) -> Path:
    source_path = data_dir / f"C_{rank}_gamma.json"
    with source_path.open(encoding="utf-8") as source:
        gamma_data = json.load(source)
    parameters = [
        parameter
        for row in gamma_data["inhomogeneous_deformation"]["gb_matrix"]["values"]
        for parameter in row
    ]
    assignment = {parameter: 1 for parameter in parameters}
    path = data_dir / f"C_{rank}_evaluated.json"
    path.write_text(
        json.dumps(evaluate_gamma(gamma_data, assignment), indent=2) + "\n",
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    for rank in (1, 2, 3):
        print(write_evaluated(rank, root / "data"))
