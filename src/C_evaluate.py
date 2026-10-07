#!/usr/bin/env python3
"""Evaluate Schema 2 gamma coefficients for an approved C(n+1) gb profile."""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from fractions import Fraction
from pathlib import Path
from typing import Any


_TERM = re.compile(r"([+-]?)(?:(\d+(?:/\d+)?)\*)?(gb_[A-Za-z0-9_]+)")


def _parse_coefficient(expression: str, parameters: set[str]) -> dict[str, Fraction]:
    compact = expression.replace(" ", "")
    coefficients: dict[str, Fraction] = {}
    position = 0
    while position < len(compact):
        match = _TERM.match(compact, position)
        if match is None or (position > 0 and match.group(1) not in ("+", "-")):
            raise ValueError(f"Invalid symbolic gamma coefficient: {expression!r}")
        sign, magnitude, parameter = match.groups()
        if parameter not in parameters:
            raise ValueError(
                f"Gamma coefficient references unknown gb parameter {parameter!r}"
            )
        coefficient = Fraction(magnitude or "1")
        if sign == "-":
            coefficient = -coefficient
        coefficients[parameter] = coefficients.get(parameter, Fraction()) + coefficient
        position = match.end()
    return {
        parameter: coefficient
        for parameter, coefficient in coefficients.items()
        if coefficient
    }


def _fraction_string(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else str(value)


def _parameter_order(schema2: dict[str, Any]) -> list[str]:
    gb_matrix = schema2.get("gb_matrix")
    if not isinstance(gb_matrix, dict):
        raise ValueError("Schema 2 must contain a gb_matrix object")
    parameters = gb_matrix.get("parameter_order")
    if (
        not isinstance(parameters, list)
        or not parameters
        or not all(isinstance(parameter, str) for parameter in parameters)
        or len(set(parameters)) != len(parameters)
    ):
        raise ValueError("Schema 2 gb_matrix.parameter_order is invalid")
    return parameters


def _validate_inputs(n: int, schema1: dict[str, Any], schema2: dict[str, Any]) -> list[str]:
    if schema1.get("algebra", {}).get("n") != n:
        raise ValueError(f"Schema 1 rank does not match n={n}")
    if schema2.get("algebra") != schema1.get("algebra"):
        raise ValueError(f"Schema 2 algebra does not match Schema 1 for n={n}")
    if schema2.get("source_schema") != f"C_{n}_structure.json":
        raise ValueError(f"Schema 2 source_schema is inconsistent for n={n}")
    parameters = _parameter_order(schema2)
    gamma_records = schema2.get("inhomogeneous_deformation", {}).get(
        "gamma_structure"
    )
    if not isinstance(gamma_records, list):
        raise ValueError("Schema 2 must contain an inhomogeneous gamma_structure list")

    parity = schema1.get("parity")
    basis_names = set(schema1.get("basis", {}).get("even", [])) | set(
        schema1.get("basis", {}).get("odd", [])
    )
    if not isinstance(parity, dict) or set(parity) != basis_names:
        raise ValueError("Schema 1 basis and parity map are inconsistent")
    allowed_outputs = basis_names | {"K"}
    parameter_set = set(parameters)
    for index, record in enumerate(gamma_records):
        if not isinstance(record, dict) or not all(
            key in record for key in ("X", "Y", "Z", "coeff", "sign_rule")
        ):
            raise ValueError(f"Schema 2 gamma_structure[{index}] is malformed")
        if (
            record["X"] not in basis_names
            or record["Y"] not in basis_names
            or record["Z"] not in allowed_outputs
            or record["sign_rule"] != "graded"
            or not isinstance(record["coeff"], str)
        ):
            raise ValueError(f"Schema 2 gamma_structure[{index}] has invalid fields")
        output_parity = parity.get(record["Z"], 0)
        if output_parity != (parity[record["X"]] + parity[record["Y"]] + 1) % 2:
            raise ValueError(
                f"Schema 2 gamma_structure[{index}] has inconsistent parity"
            )
        _parse_coefficient(record["coeff"], parameter_set)
    return parameters


def build_evaluated_schema(
    n: int,
    schema1: dict[str, Any],
    schema2: dict[str, Any],
    generation_date: str | None = None,
) -> dict[str, Any]:
    """Build Schema 3 for the uniform all-positive gb assignment."""
    if n not in (1, 2, 3):
        raise ValueError(f"Unsupported bosonic rank n={n}; expected 1, 2, or 3")
    parameters = _validate_inputs(n, schema1, schema2)
    assignment = {parameter: 1 for parameter in parameters}
    evaluated_records = []
    for record in schema2["inhomogeneous_deformation"]["gamma_structure"]:
        value = sum(
            (
                coefficient * assignment[parameter]
                for parameter, coefficient in _parse_coefficient(
                    record["coeff"], set(parameters)
                ).items()
            ),
            Fraction(),
        )
        if value:
            evaluated_records.append(
                {
                    "X": record["X"],
                    "Y": record["Y"],
                    "Z": record["Z"],
                    "coeff": _fraction_string(value),
                    "sign_rule": record["sign_rule"],
                }
            )

    gamma_deformation = schema2["inhomogeneous_deformation"]
    metadata = schema2.get("metadata", {})
    return {
        "schema_version": schema1["schema_version"],
        "schema_layer": 3,
        "algebra": schema1["algebra"],
        "source_schema": f"C_{n}_structure.json",
        "source_gamma_schema": f"C_{n}_gamma.json",
        "gb_assignment": {
            "profile": "uniform_all_positive",
            "parameter_order": parameters,
            "values": assignment,
        },
        "structure_constants": schema1["structure_constants"],
        "inhomogeneous_deformation": {
            "central_symbol": gamma_deformation["central_symbol"],
            "central_parity": gamma_deformation["central_parity"],
            "gamma_structure": evaluated_records,
        },
        "metadata": {
            "generated_by": "C_evaluate.py",
            "generation_date": generation_date
            or metadata.get("generation_date")
            or date.today().isoformat(),
            "references": [
                f"C_{n}_structure.json",
                f"C_{n}_gamma.json",
                "Approved uniform all-positive gb assignment",
            ],
        },
    }


def write_evaluated_schema(
    n: int,
    output_dir: Path,
    source_dir: Path | None = None,
) -> Path:
    source_dir = source_dir or output_dir
    schema1_path = source_dir / f"C_{n}_structure.json"
    schema2_path = source_dir / f"C_{n}_gamma.json"
    for path in (schema1_path, schema2_path):
        if not path.is_file():
            raise FileNotFoundError(f"Schema source file not found: {path}")
    schema1 = json.loads(schema1_path.read_text(encoding="utf-8"))
    schema2 = json.loads(schema2_path.read_text(encoding="utf-8"))
    result = build_evaluated_schema(n, schema1, schema2)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"C_{n}_evaluated.json"
    output_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate evaluated C(n+1) Schema 3 JSON files."
    )
    parser.add_argument(
        "n",
        nargs="*",
        type=int,
        choices=(1, 2, 3),
        default=None,
        help="bosonic rank(s) to generate; defaults to 1, 2, and 3",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "data",
        help="directory for generated evaluated JSON files",
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=None,
        help="directory containing Schema 1 and Schema 2 source files",
    )
    args = parser.parse_args()
    for n in args.n or (1, 2, 3):
        print(write_evaluated_schema(n, args.output_dir, args.source_dir))


if __name__ == "__main__":
    main()
