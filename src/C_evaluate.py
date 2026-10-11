#!/usr/bin/env python3
"""Evaluate C(n+1) gamma data for the approved checkerboard gb profile."""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from fractions import Fraction
from pathlib import Path
from typing import Any

_PROFILE_NAME = "alternating_checkerboard"
_PROFILE_FORMULA = (
    "gb_a1_p_b{j}_p=(-1)^(j-1), gb_a1_p_b{j}_m=(-1)^j, "
    "gb_a1_m_b{j}_p=(-1)^j, gb_a1_m_b{j}_m=(-1)^(j-1), j=1,...,n"
)


def _basis_labels(schema1: dict[str, Any]) -> list[str]:
    try:
        basis = schema1["basis"]
        return list(basis["odd"]) + list(basis["even"])
    except (KeyError, TypeError) as error:
        raise ValueError(f"Malformed Schema 1 basis: {error}") from error


def _validate_gamma_matrix(
    schema2: dict[str, Any],
    n: int,
) -> tuple[list[list[str]], list[list[int]]]:
    try:
        matrix = schema2["gb_matrix"]
        shape = matrix["shape"]
        row_labels = matrix["row_labels"]
        column_labels = matrix["column_labels"]
        parameters = matrix["parameters"]
        parity = matrix["parity"]
    except (KeyError, TypeError) as error:
        raise ValueError(f"Malformed Schema 2 gb_matrix: {error}") from error

    expected_columns = [
        label
        for index in range(1, n + 1)
        for label in (f"b_{index}_p", f"b_{index}_m")
    ]
    expected_rows = ["a_1_p", "a_1_m"]
    if shape != [2, 2 * n]:
        raise ValueError(f"Schema 2 gb_matrix shape must be [2, {2 * n}]")
    if row_labels != expected_rows or column_labels != expected_columns:
        raise ValueError("Schema 2 gb_matrix labels do not match the C(n+1) ordering")
    if parity != 0:
        raise ValueError("Schema 2 gb parameters must have parity 0")
    if len(parameters) != 2 or any(len(row) != 2 * n for row in parameters):
        raise ValueError("Schema 2 gb parameter matrix has incorrect dimensions")

    for row_index, row_label in enumerate(expected_rows):
        for column_index, column_label in enumerate(expected_columns):
            _, boson_index, boson_sign = column_label.split("_")
            expected_parameter = (
                f"gb_a1_{row_label[-1]}_b{boson_index}_{boson_sign}"
            )
            if parameters[row_index][column_index] != expected_parameter:
                raise ValueError(
                    "Unexpected Schema 2 gb parameter at "
                    f"({row_index}, {column_index}): {parameters[row_index][column_index]}"
                )

    values = [
        [
            (-1) ** (
                row_index
                + column_index // 2
                + column_index % 2
            )
            for column_index in range(2 * n)
        ]
        for row_index in range(2)
    ]
    return parameters, values


def _parse_linear_coefficient(
    expression: str,
    parameter_values: dict[str, int],
) -> Fraction:
    """Evaluate an exact linear expression in gb parameters."""
    if not isinstance(expression, str) or not expression:
        raise ValueError(f"Gamma coefficient must be a nonempty string: {expression!r}")

    parts = re.split(r" ([+-]) ", expression)
    if len(parts) % 2 == 0:
        raise ValueError(f"Malformed gamma coefficient expression: {expression}")

    result = Fraction()
    for index in range(0, len(parts), 2):
        sign = 1 if index == 0 or parts[index - 1] == "+" else -1
        term = parts[index]
        if index == 0 and term.startswith("-"):
            sign *= -1
            term = term[1:]
        if "*" in term:
            scalar_text, parameter = term.split("*", maxsplit=1)
            try:
                scalar = Fraction(scalar_text)
            except (ValueError, ZeroDivisionError) as error:
                raise ValueError(
                    f"Invalid scalar in gamma coefficient: {term}"
                ) from error
        else:
            scalar, parameter = Fraction(1), term
        if parameter not in parameter_values:
            raise ValueError(f"Unknown gb parameter in gamma coefficient: {parameter}")
        result += sign * scalar * parameter_values[parameter]
    return result


def _read_structure_constants(
    records: Any,
    allowed_labels: set[str],
    coefficient_field: str,
) -> dict[tuple[str, str, str], Fraction]:
    if not isinstance(records, list):
        raise ValueError(f"{coefficient_field} records must be an array")

    result: dict[tuple[str, str, str], Fraction] = {}
    for record in records:
        try:
            x, y, z = record["X"], record["Y"], record["Z"]
            coefficient = Fraction(record[coefficient_field])
        except (KeyError, TypeError, ValueError, ZeroDivisionError) as error:
            raise ValueError(f"Malformed {coefficient_field} record: {record}") from error
        if x not in allowed_labels or y not in allowed_labels or z not in allowed_labels:
            raise ValueError(f"Structure record contains an unknown label: {record}")
        key = (x, y, z)
        if key in result:
            raise ValueError(f"Duplicate structure record: {record}")
        if coefficient:
            result[key] = coefficient
        else:
            raise ValueError(f"Structure records must be nonzero: {record}")
    return result


def evaluate_schema(
    schema1: dict[str, Any],
    schema2: dict[str, Any],
    generation_date: str | None = None,
) -> dict[str, Any]:
    """Substitute the checkerboard profile and combine base and gamma parts."""
    try:
        algebra = schema1["algebra"]
        n = algebra["n"]
        if algebra["family"] != "C" or algebra["m"] != 1:
            raise ValueError("Schema 1 input must describe C(n+1) with m=1")
        if schema2["algebra"] != algebra:
            raise ValueError("Schema 2 algebra does not match Schema 1")
        if schema2["metadata"]["schema1_file"] != f"C_{n}_structure.json":
            raise ValueError("Schema 2 metadata references the wrong Schema 1 file")
    except (KeyError, TypeError) as error:
        raise ValueError(f"Malformed input schema: {error}") from error
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        raise ValueError("Schema rank n must be a positive integer")

    labels = _basis_labels(schema1)
    label_set = set(labels)
    parameters, values = _validate_gamma_matrix(schema2, n)
    parameter_values = {
        parameter: values[row_index][column_index]
        for row_index, row in enumerate(parameters)
        for column_index, parameter in enumerate(row)
    }

    base_records = _read_structure_constants(
        schema1.get("structure_constants"),
        label_set,
        "coeff",
    )
    try:
        gamma_records = schema2["inhomogeneous_deformation"]["gamma_structure"]
    except (KeyError, TypeError) as error:
        raise ValueError(f"Malformed Schema 2 gamma structure: {error}") from error
    if not isinstance(gamma_records, list):
        raise ValueError("Schema 2 gamma_structure must be an array")

    allowed_gamma_outputs = label_set | {"K"}
    evaluated_gamma: dict[tuple[str, str, str], Fraction] = {}
    for record in gamma_records:
        try:
            x, y, z = record["X"], record["Y"], record["Z"]
            if record["sign_rule"] != "graded":
                raise ValueError("Gamma record must use the graded sign rule")
            coefficient = _parse_linear_coefficient(
                record["coeff"],
                parameter_values,
            )
        except (KeyError, TypeError) as error:
            raise ValueError(f"Malformed Schema 2 gamma record: {record}") from error
        if x not in label_set or y not in label_set or z not in allowed_gamma_outputs:
            raise ValueError(f"Schema 2 gamma record contains an unknown label: {record}")
        key = (x, y, z)
        if key in evaluated_gamma:
            raise ValueError(f"Duplicate Schema 2 gamma record: {record}")
        if coefficient:
            evaluated_gamma[key] = coefficient

    output_labels = labels + ["K"]
    order = {label: index for index, label in enumerate(output_labels)}
    all_keys = set(base_records) | set(evaluated_gamma)
    evaluated_records = []
    for x, y, z in sorted(
        all_keys,
        key=lambda item: (order[item[0]], order[item[1]], order[item[2]]),
    ):
        base_coefficient = base_records.get((x, y, z), Fraction())
        kappa_coefficient = evaluated_gamma.get((x, y, z), Fraction())
        if base_coefficient or kappa_coefficient:
            evaluated_records.append({
                "X": x,
                "Y": y,
                "Z": z,
                "base_coeff": str(base_coefficient),
                "kappa_coeff": str(kappa_coefficient),
                "sign_rule": "graded",
            })

    matrix = schema2["gb_matrix"]
    return {
        "schema_version": schema2["schema_version"],
        "algebra": algebra,
        "gb_matrix": {
            "shape": matrix["shape"],
            "row_labels": matrix["row_labels"],
            "column_labels": matrix["column_labels"],
            "parameters": parameters,
            "values": values,
            "parity": matrix["parity"],
        },
        "parameter_profile": {
            "name": _PROFILE_NAME,
            "formula": _PROFILE_FORMULA,
        },
        "evaluated_structure_constants": evaluated_records,
        "metadata": {
            "generated_by": "C_evaluate.py",
            "source_schema1_file": f"C_{n}_structure.json",
            "source_schema2_file": f"C_{n}_gamma.json",
            "generation_date": generation_date or date.today().isoformat(),
        },
    }


def write_evaluated_schema(
    schema1: dict[str, Any],
    schema2: dict[str, Any],
    output_dir: str | Path,
    generation_date: str | None = None,
) -> Path:
    """Write `C_{n}_evaluated.json`."""
    n = schema1["algebra"]["n"]
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    destination = output_path / f"C_{n}_evaluated.json"
    serialized = json.dumps(
        evaluate_schema(schema1, schema2, generation_date),
        ensure_ascii=False,
        indent=2,
    )
    destination.write_text(serialized + "\n", encoding="utf-8")
    return destination


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate C(n+1) gamma data for the checkerboard gb profile."
    )
    parser.add_argument(
        "--ranks",
        type=int,
        nargs="+",
        default=[1, 2, 3],
        help="Bosonic ranks to generate (default: 1 2 3).",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data",
        help="Directory containing the Schema 1 and Schema 2 inputs.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data",
        help="Directory for C_n_evaluated.json outputs.",
    )
    args = parser.parse_args(argv)

    for n in args.ranks:
        schema1_path = args.data_dir / f"C_{n}_structure.json"
        schema2_path = args.data_dir / f"C_{n}_gamma.json"
        try:
            schema1 = json.loads(schema1_path.read_text(encoding="utf-8"))
            schema2 = json.loads(schema2_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            parser.error(
                f"could not load Schema 1/2 inputs for n={n}: {error}"
            )
        destination = write_evaluated_schema(
            schema1,
            schema2,
            args.output_dir,
        )
        print(f"Wrote {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
