"""Evaluate C(n+1) gamma data at a representative gb assignment."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


def evaluate_schema(
    structure: dict[str, Any],
    gamma_schema: dict[str, Any],
    assignment: dict[str, int] | None = None,
) -> dict[str, Any]:
    n = structure["algebra"]["n"]
    if gamma_schema["algebra"]["n"] != n:
        raise ValueError("Schema 1 and Schema 2 ranks do not match.")
    if gamma_schema["algebra"]["base_structure_file"] != f"C_{n}_structure.json":
        raise ValueError("Schema 2 references a different Schema 1 file.")

    parameter_names = [
        parameter
        for row in gamma_schema["gb_matrix"]["parameters"]
        for parameter in row
    ]
    if assignment is None:
        assignment = {parameter: 1 for parameter in parameter_names}
    if set(assignment) != set(parameter_names):
        raise ValueError("The assignment must provide exactly all gb parameters.")
    if any(value not in (-1, 1) for value in assignment.values()):
        raise ValueError("Each representative gb value must be +1 or -1.")

    combined: dict[tuple[str, str, str], dict[str, Fraction]] = {}
    for entry in structure["structure_constants"]:
        key = (entry["X"], entry["Y"], entry["Z"])
        values = combined.setdefault(key, {"base": Fraction(0), "gamma": Fraction(0)})
        values["base"] += Fraction(entry["coeff"])
    for entry in gamma_schema["inhomogeneous_deformation"]["gamma_coefficients"]:
        key = (entry["X"], entry["Y"], entry["Z"])
        values = combined.setdefault(key, {"base": Fraction(0), "gamma": Fraction(0)})
        values["gamma"] += Fraction(entry["coeff"]) * assignment[entry["parameter"]]

    evaluated = [
        {
            "X": x,
            "Y": y,
            "Z": z,
            "base_coeff": _fraction_text(values["base"]),
            "kappa_coeff": _fraction_text(values["gamma"]),
            "evaluated_coefficient": (
                f"{_fraction_text(values['base'])} + kappa * "
                f"({_fraction_text(values['gamma'])})"
            ),
            "sign_rule": "graded",
        }
        for (x, y, z), values in sorted(combined.items())
        if values["base"] or values["gamma"]
    ]
    return {
        "schema_version": "5.0",
        "layer": 3,
        "algebra": structure["algebra"],
        "base_structure_file": f"C_{n}_structure.json",
        "gamma_source_file": f"C_{n}_gamma.json",
        "parameter_assignment": assignment,
        "assignment_profile": (
            "all_plus_one" if all(value == 1 for value in assignment.values()) else "custom"
        ),
        "evaluated_structure_constants": evaluated,
        "metadata": {
            "generated_by": "src/evaluate_C.py",
            "evaluation": "Exact substitution into the first-order kappa expansion.",
            "source_assumptions": gamma_schema["metadata"]["assumptions"],
        },
    }


def _fraction_text(value: Fraction) -> str:
    return str(value)


def validate_evaluation(
    evaluated: dict[str, Any],
    structure: dict[str, Any],
    gamma_schema: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    if evaluated["algebra"]["n"] != structure["algebra"]["n"]:
        errors.append("Evaluated rank does not match Schema 1.")
    if evaluated["gamma_source_file"] != f"C_{structure['algebra']['n']}_gamma.json":
        errors.append("Evaluated data references the wrong gamma file.")
    parameters = set(evaluated["parameter_assignment"])
    expected_parameters = {
        parameter
        for row in gamma_schema["gb_matrix"]["parameters"]
        for parameter in row
    }
    if parameters != expected_parameters:
        errors.append("Evaluated assignment does not match the Schema 2 gb matrix.")
    available = set(structure["parity"]) | {"K"}
    for entry in evaluated["evaluated_structure_constants"]:
        if any(entry[field] not in available for field in ("X", "Y", "Z")):
            errors.append(f"Evaluated bracket references an unknown Schema 1 label: {entry}.")
    expected: dict[tuple[str, str, str], dict[str, Fraction]] = {}
    for entry in structure["structure_constants"]:
        key = (entry["X"], entry["Y"], entry["Z"])
        expected.setdefault(key, {"base": Fraction(0), "gamma": Fraction(0)})
        expected[key]["base"] += Fraction(entry["coeff"])
    for entry in gamma_schema["inhomogeneous_deformation"]["gamma_coefficients"]:
        key = (entry["X"], entry["Y"], entry["Z"])
        expected.setdefault(key, {"base": Fraction(0), "gamma": Fraction(0)})
        expected[key]["gamma"] += Fraction(entry["coeff"]) * evaluated["parameter_assignment"][
            entry["parameter"]
        ]
    actual: dict[tuple[str, str, str], dict[str, Fraction]] = {}
    for entry in evaluated["evaluated_structure_constants"]:
        key = (entry["X"], entry["Y"], entry["Z"])
        if key in actual:
            errors.append(f"Duplicate evaluated bracket entry: {key}.")
        base_coeff = Fraction(entry["base_coeff"])
        gamma_coeff = Fraction(entry["kappa_coeff"])
        expected_text = f"{_fraction_text(base_coeff)} + kappa * ({_fraction_text(gamma_coeff)})"
        if entry["evaluated_coefficient"] != expected_text:
            errors.append(f"Rendered coefficient does not match exact values: {key}.")
        actual[key] = {"base": base_coeff, "gamma": gamma_coeff}
    if actual != {key: value for key, value in expected.items() if any(value.values())}:
        errors.append("Evaluated coefficients do not equal Schema 1 plus substituted Schema 2.")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ranks", nargs="+", type=int, default=[1, 2, 3])
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    args = parser.parse_args()
    failed = False
    for n in args.ranks:
        structure = json.loads(
            (args.data_dir / f"C_{n}_structure.json").read_text(encoding="utf-8")
        )
        gamma_schema = json.loads(
            (args.data_dir / f"C_{n}_gamma.json").read_text(encoding="utf-8")
        )
        evaluated = evaluate_schema(structure, gamma_schema)
        errors = validate_evaluation(evaluated, structure, gamma_schema)
        if errors:
            for error in errors:
                print(f"FAIL C_{n}_evaluated.json: {error}")
            failed = True
            continue
        output = args.data_dir / f"C_{n}_evaluated.json"
        output.write_text(
            json.dumps(evaluated, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(
            f"PASS {output}: assignment={len(evaluated['parameter_assignment'])} values (+1), "
            f"evaluated_terms={len(evaluated['evaluated_structure_constants'])}"
        )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
