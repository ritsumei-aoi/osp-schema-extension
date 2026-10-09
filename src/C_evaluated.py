#!/usr/bin/env python3
"""Generate Schema 3 evaluated deformation data for C(n+1)."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import date
from fractions import Fraction
from pathlib import Path

SUPPORTED_RANKS = {1, 2, 3}
PROFILE_NAME = "all_positive"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"


def _expected_gb_matrix(n: int) -> tuple[list[str], list[str], list[list[str]]]:
    columns = [
        label
        for index in range(1, n + 1)
        for label in (f"b_{index}_p", f"b_{index}_m")
    ]
    entries = []
    for fermion in ("p", "m"):
        row = []
        for column in columns:
            _, index, sign = column.split("_")
            row.append(f"gb_a1{fermion}_b{index}{sign}")
        entries.append(row)
    return ["a_1_p", "a_1_m"], columns, entries


def _parse_linear_coefficient(
    expression: object,
    parameter_values: dict[str, int],
) -> Fraction:
    if not isinstance(expression, str) or not expression.strip():
        raise ValueError("Gamma coefficient must be a nonempty symbolic string.")

    total = Fraction(0)
    normalized = expression.replace("- ", "+ -")
    for piece in normalized.split(" + "):
        piece = piece.strip()
        if not piece:
            raise ValueError(f"Malformed gamma coefficient {expression!r}.")
        sign = -1 if piece.startswith("-") else 1
        unsigned = piece[1:] if sign < 0 else piece
        if "*" in unsigned:
            coefficient_text, parameter = unsigned.split("*", 1)
            try:
                coefficient = Fraction(coefficient_text)
            except (ValueError, ZeroDivisionError) as error:
                raise ValueError(
                    f"Malformed rational in gamma coefficient {expression!r}."
                ) from error
        else:
            coefficient = Fraction(1)
            parameter = unsigned
        if parameter not in parameter_values:
            raise ValueError(
                f"Unknown gb parameter {parameter!r} in {expression!r}."
            )
        total += sign * coefficient * parameter_values[parameter]
    return total


def _evaluate_gamma_coefficients(
    n: int,
    gamma_schema: dict[str, object],
    parameter_values: dict[str, int],
    schema1: dict[str, object],
) -> list[dict[str, str]]:
    try:
        deformation = gamma_schema["inhomogeneous_deformation"]
        matrix = deformation["gb_matrix"]
        gamma_records = deformation["gamma_coefficients"]
        basis = schema1["basis"]
    except (KeyError, TypeError) as error:
        raise ValueError("Schema 1 or Schema 2 is missing required fields.") from error

    if (
        not isinstance(deformation, dict)
        or not isinstance(matrix, dict)
        or not isinstance(gamma_records, list)
        or not isinstance(basis, dict)
        or not isinstance(basis.get("even"), list)
        or not isinstance(basis.get("odd"), list)
        or not all(
            isinstance(label, str)
            for label in basis["even"] + basis["odd"]
        )
    ):
        raise ValueError("Schema 1 or Schema 2 has invalid field types.")
    rows, columns, expected_entries = _expected_gb_matrix(n)
    if (
        matrix.get("rows") != rows
        or matrix.get("columns") != columns
        or matrix.get("entries") != expected_entries
    ):
        raise ValueError(f"Schema 2 gb_matrix is invalid for rank n={n}.")
    parameters = [parameter for row in expected_entries for parameter in row]
    if set(parameter_values) != set(parameters):
        raise ValueError("Evaluation profile must assign every gb parameter exactly once.")

    basis_labels = set(basis["even"] + basis["odd"])
    valid_outputs = basis_labels | {"K"}
    evaluated: dict[tuple[str, str, str], Fraction] = defaultdict(Fraction)
    for record in gamma_records:
        if not isinstance(record, dict):
            raise ValueError("Schema 2 gamma records must be objects.")
        try:
            left, right, output = record["X"], record["Y"], record["Z"]
            expression, sign_rule = record["coeff"], record["sign_rule"]
        except KeyError as error:
            raise ValueError("Schema 2 gamma record is missing a required field.") from error
        if (
            not all(isinstance(label, str) for label in (left, right, output))
            or left not in basis_labels
            or right not in basis_labels
            or output not in valid_outputs
            or sign_rule != "graded"
        ):
            raise ValueError(f"Invalid Schema 2 gamma record: {record!r}.")
        coefficient = _parse_linear_coefficient(expression, parameter_values)
        evaluated[(left, right, output)] += coefficient

    return [
        {"X": left, "Y": right, "Z": output, "coeff": str(coefficient), "sign_rule": "graded"}
        for (left, right, output), coefficient in evaluated.items()
        if coefficient
    ]


def _verify_evaluation(
    schema1: dict[str, object],
    gamma_schema: dict[str, object],
    evaluated_schema: dict[str, object],
    expected_records: list[dict[str, str]],
    parameter_values: dict[str, int],
) -> None:
    if evaluated_schema.get("structure_constants") != schema1.get("structure_constants"):
        raise ValueError("Evaluated Schema 3 changed the undeformed structure constants.")
    if evaluated_schema.get("basis") != schema1.get("basis"):
        raise ValueError("Evaluated Schema 3 changed the Schema 1 basis.")
    if evaluated_schema.get("parity") != schema1.get("parity"):
        raise ValueError("Evaluated Schema 3 changed the Schema 1 parity map.")
    try:
        evaluated_deformation = evaluated_schema["inhomogeneous_deformation"]
        source_deformation = gamma_schema["inhomogeneous_deformation"]
    except (KeyError, TypeError) as error:
        raise ValueError("Evaluated Schema 3 is missing its deformation data.") from error
    if evaluated_deformation["evaluated_gamma_coefficients"] != expected_records:
        raise ValueError("Evaluated gamma coefficients disagree with Schema 2 substitution.")
    if evaluated_deformation["evaluation_profile"] != {
        "name": PROFILE_NAME,
        "parameter_values": parameter_values,
    }:
        raise ValueError("Evaluated Schema 3 does not record the selected gb profile.")
    if evaluated_deformation["gb_matrix"] != source_deformation["gb_matrix"]:
        raise ValueError("Evaluated Schema 3 changed the Schema 2 gb matrix.")
    if any(
        record["Z"] == "K"
        for record in source_deformation["gamma_coefficients"]
    ) and not any(
        record["Z"] == "K"
        for record in evaluated_deformation["evaluated_gamma_coefficients"]
    ):
        raise ValueError("Evaluated Schema 3 lost every central K output.")


def build_evaluated_schema(
    n: int,
    data_dir: Path | None = None,
    generation_date: str | None = None,
) -> dict[str, object]:
    if n not in SUPPORTED_RANKS:
        raise ValueError("This evaluator supports bosonic ranks n=1, 2, and 3.")
    root = data_dir or DATA_DIR
    schema1_path = root / f"C_{n}_structure.json"
    gamma_path = root / f"C_{n}_gamma.json"
    schema1 = json.loads(schema1_path.read_text(encoding="utf-8"))
    gamma_schema = json.loads(gamma_path.read_text(encoding="utf-8"))
    if schema1["algebra"] != gamma_schema["algebra"] or schema1["algebra"]["n"] != n:
        raise ValueError(f"Schema 1 and Schema 2 algebra metadata disagree for n={n}.")

    _, _, entries = _expected_gb_matrix(n)
    parameter_values = {parameter: 1 for row in entries for parameter in row}
    evaluated_records = _evaluate_gamma_coefficients(
        n, gamma_schema, parameter_values, schema1
    )
    source_deformation = gamma_schema["inhomogeneous_deformation"]
    evaluated_schema = dict(schema1)
    evaluated_schema["inhomogeneous_deformation"] = {
        "output_space": source_deformation["output_space"],
        "gb_matrix": source_deformation["gb_matrix"],
        "deformed_oscillator_relations": source_deformation[
            "deformed_oscillator_relations"
        ],
        "evaluation_profile": {
            "name": PROFILE_NAME,
            "parameter_values": parameter_values,
        },
        "evaluated_gamma_coefficients": evaluated_records,
    }
    evaluated_schema["metadata"] = {
        "generated_by": "C_evaluated.py",
        "generation_date": generation_date or date.today().isoformat(),
        "references": [
            f"data/C_{n}_structure.json",
            f"data/C_{n}_gamma.json",
            "docs/math/C_inhomogeneous_definition.md",
        ],
    }
    _verify_evaluation(
        schema1,
        gamma_schema,
        evaluated_schema,
        evaluated_records,
        parameter_values,
    )
    return evaluated_schema


def output_path(n: int, data_dir: Path | None = None) -> Path:
    if n not in SUPPORTED_RANKS:
        raise ValueError("This evaluator supports bosonic ranks n=1, 2, and 3.")
    return (data_dir or DATA_DIR) / f"C_{n}_evaluated.json"


def write_evaluated_schema(n: int, data_dir: Path | None = None) -> Path:
    schema = build_evaluated_schema(n, data_dir)
    path = output_path(n, data_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(schema, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "n",
        type=int,
        nargs="*",
        default=[1, 2, 3],
        help="Bosonic rank(s) to generate (default: 1 2 3).",
    )
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    args = parser.parse_args()
    for rank in args.n:
        print(write_evaluated_schema(rank, args.data_dir))


if __name__ == "__main__":
    main()
