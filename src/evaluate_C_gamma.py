"""Substitute the all-positive gb profile into C(n+1) Schema 2 data."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path


def _format_coefficient(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def evaluate_schema(n: int, data_dir: Path = Path("data")) -> dict:
    if n < 1:
        raise ValueError("n must be a positive integer")

    structure_path = data_dir / f"C_{n}_structure.json"
    gamma_path = data_dir / f"C_{n}_gamma.json"
    structure = json.loads(structure_path.read_text(encoding="utf-8"))
    gamma_schema = json.loads(gamma_path.read_text(encoding="utf-8"))
    if structure["algebra"]["n"] != n or gamma_schema["algebra"]["n"] != n:
        raise ValueError(f"rank mismatch in Schema 1 or Schema 2 data for n={n}")

    deformation = gamma_schema["inhomogeneous_deformation"]
    parameters = [
        parameter["name"] for parameter in gamma_schema["gb_matrix"]["parameters"]
    ]
    assignment = {parameter: 1 for parameter in parameters}
    if len(assignment) != 4 * n:
        raise ValueError(f"expected exactly {4 * n} unique gb parameters for n={n}")

    undeformed: dict[tuple[str, str, str], Fraction] = {}
    for term in structure["structure_constants"]:
        key = (term["X"], term["Y"], term["Z"])
        undeformed[key] = undeformed.get(key, Fraction(0)) + Fraction(term["coeff"])

    evaluated_gamma: dict[tuple[str, str, str], Fraction] = {}
    for term in deformation["gamma_coefficients"]:
        parameter = term["gb_parameter"]
        if parameter not in assignment:
            raise ValueError(f"unknown gb parameter in Schema 2: {parameter}")
        key = (term["X"], term["Y"], term["Z"])
        evaluated_gamma[key] = evaluated_gamma.get(key, Fraction(0)) + (
            Fraction(term["coeff"]) * assignment[parameter]
        )

    ordered_keys = list(dict.fromkeys([*undeformed, *evaluated_gamma]))
    evaluated_constants = []
    for x, y, z in ordered_keys:
        base_coeff = undeformed.get((x, y, z), Fraction(0))
        gamma_coeff = evaluated_gamma.get((x, y, z), Fraction(0))
        if not base_coeff and not gamma_coeff:
            continue
        evaluated_constants.append(
            {
                "X": x,
                "Y": y,
                "Z": z,
                "undeformed_coeff": _format_coefficient(base_coeff),
                "kappa_coeff": _format_coefficient(gamma_coeff),
                "sign_rule": "graded",
            }
        )

    return {
        "schema_version": "5.0",
        "algebra": structure["algebra"],
        "basis": structure["basis"],
        "parity": structure["parity"],
        "evaluation": {
            "profile": "all_positive",
            "description": "Set every gb parameter to +1.",
            "gb_assignment": assignment,
        },
        "structure_constants": evaluated_constants,
        "inhomogeneous_deformation": {
            "kappa": deformation["kappa"],
            "evaluated_gamma_coefficients": [
                {
                    "X": x,
                    "Y": y,
                    "Z": z,
                    "coeff": _format_coefficient(coeff),
                    "sign_rule": "graded",
                }
                for (x, y, z), coeff in evaluated_gamma.items()
                if coeff
            ],
            "symbolic_term_count": len(deformation["gamma_coefficients"]),
            "evaluated_term_count": sum(bool(coeff) for coeff in evaluated_gamma.values()),
            "consistency": deformation["consistency"],
        },
        "metadata": {
            "generated_by": "src/evaluate_C_gamma.py",
            "generation_date": structure["metadata"]["generation_date"],
            "references": [
                f"data/C_{n}_structure.json",
                f"data/C_{n}_gamma.json",
            ],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ranks", nargs="+", type=int, default=[1, 2, 3])
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    args = parser.parse_args()

    for n in args.ranks:
        evaluated = evaluate_schema(n, args.data_dir)
        output = args.data_dir / f"C_{n}_evaluated.json"
        output.write_text(
            json.dumps(evaluated, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"Wrote {output}")


if __name__ == "__main__":
    main()
