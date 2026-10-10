"""Evaluate C(n+1) Schema 2 gamma coefficients for a sign profile."""

from __future__ import annotations

import argparse
import json
from datetime import date
from fractions import Fraction
from pathlib import Path

import sympy as sp


def checkerboard_assignment(n: int) -> tuple[list[list[int]], dict[str, int]]:
    if n < 1:
        raise ValueError("n must be a positive integer")

    rows = ["a_1_p", "a_1_m"]
    columns = [
        label
        for k in range(1, n + 1)
        for label in (f"b_{k}_p", f"b_{k}_m")
    ]
    values = [
        [1 if (row + column) % 2 == 0 else -1 for column in range(2 * n)]
        for row in range(2)
    ]
    assignment = {
        f"gb_a1_{'p' if row == 0 else 'm'}_b{column_label.split('_')[1]}_{column_label.split('_')[2]}": values[row][column]
        for row in range(2)
        for column, column_label in enumerate(columns)
    }
    return values, assignment


def _fraction_string(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _evaluate_coefficient(expression: str, assignment: dict[str, int]) -> Fraction:
    evaluated = sp.sympify(
        expression,
        locals={name: sp.Integer(value) for name, value in assignment.items()},
    )
    if evaluated.free_symbols:
        unknown = sorted(str(symbol) for symbol in evaluated.free_symbols)
        raise ValueError(f"Unassigned symbols in coefficient {expression!r}: {unknown}")
    if not evaluated.is_Rational:
        raise ValueError(f"Coefficient did not evaluate to a rational: {expression!r}")
    return Fraction(int(evaluated.p), int(evaluated.q))


def _validate_gamma_skew_symmetry(
    coefficients: dict[tuple[str, str, str], Fraction],
    parity: dict[str, int],
) -> None:
    for (left, right, result), coefficient in coefficients.items():
        factor = 1 if parity[left] * parity[right] % 2 else -1
        reverse = coefficients.get((right, left, result), Fraction(0))
        if reverse != factor * coefficient:
            raise ValueError(
                f"Evaluated gamma violates graded skew-symmetry for "
                f"({left}, {right}, {result})"
            )


def evaluate_schema(
    n: int,
    structure_data: dict,
    gamma_data: dict,
    generation_date: str | None = None,
) -> dict:
    if structure_data["algebra"]["family"] != "C" or structure_data["algebra"]["n"] != n:
        raise ValueError("Schema 1 family/rank does not match requested C(n+1) rank")
    if gamma_data["algebra"]["family"] != "C" or gamma_data["algebra"]["n"] != n:
        raise ValueError("Schema 2 family/rank does not match requested C(n+1) rank")
    if gamma_data["source_structure_file"] != f"C_{n}_structure.json":
        raise ValueError("Schema 2 references the wrong Schema 1 source file")

    deformation = gamma_data["inhomogeneous_deformation"]
    matrix = deformation["gb_matrix"]
    if matrix["parameter_parity"] != 0 or deformation["kappa"]["parity"] != 1:
        raise ValueError("Schema 2 must use even gb parameters and odd kappa")
    values, assignment = checkerboard_assignment(n)
    columns = [
        label
        for k in range(1, n + 1)
        for label in (f"b_{k}_p", f"b_{k}_m")
    ]
    if matrix["row_labels"] != ["a_1_p", "a_1_m"] or matrix["column_labels"] != columns:
        raise ValueError("Schema 2 gb_matrix ordering is incompatible with the profile")
    expected_parameter_matrix = [
        [
            f"gb_a1_{'p' if row == 0 else 'm'}_b{column_label.split('_')[1]}_{column_label.split('_')[2]}"
            for column_label in columns
        ]
        for row in range(2)
    ]
    if matrix["entries"] != expected_parameter_matrix:
        raise ValueError("Schema 2 gb_matrix entries do not match their row/column labels")

    basis_labels = set(structure_data["basis"]["even"] + structure_data["basis"]["odd"])
    parity = structure_data["parity"]
    allowed_outputs = basis_labels | {"K"}
    evaluated_gamma: dict[tuple[str, str, str], Fraction] = {}
    evaluated_gamma_records = []
    for entry in deformation["gamma_coefficients"]:
        left, right, result = entry["X"], entry["Y"], entry["Z"]
        if left not in basis_labels or right not in basis_labels or result not in allowed_outputs:
            raise ValueError(f"Schema 2 gamma entry references an unknown generator: {entry}")
        key = (left, right, result)
        if key in evaluated_gamma:
            raise ValueError(f"Duplicate Schema 2 gamma coefficient for {key}")
        coefficient = _evaluate_coefficient(entry["coeff"], assignment)
        if result == "K":
            result_parity = 0
        else:
            result_parity = parity[result]
        expected_parity = (parity[left] + parity[right] + 1) % 2
        if coefficient and result_parity != expected_parity:
            raise ValueError(f"Evaluated gamma output parity mismatch for {key}")
        evaluated_gamma[key] = coefficient
        if coefficient:
            evaluated_gamma_records.append(
                {
                    "X": left,
                    "Y": right,
                    "Z": result,
                    "coeff": _fraction_string(coefficient),
                    "sign_rule": "graded",
                }
            )

    _validate_gamma_skew_symmetry(evaluated_gamma, parity)

    base_constants = {}
    for entry in structure_data["structure_constants"]:
        key = (entry["X"], entry["Y"], entry["Z"])
        if key in base_constants:
            raise ValueError(f"Duplicate Schema 1 structure constant for {key}")
        base_constants[key] = Fraction(entry["coeff"])

    labels = structure_data["basis"]["even"] + structure_data["basis"]["odd"] + ["K"]
    label_order = {label: index for index, label in enumerate(labels)}
    all_keys = set(base_constants) | set(evaluated_gamma)
    evaluated_structure = []
    for left, right, result in sorted(
        all_keys,
        key=lambda item: tuple(label_order[label] for label in item),
    ):
        base_coefficient = base_constants.get((left, right, result), Fraction(0))
        gamma_coefficient = evaluated_gamma.get((left, right, result), Fraction(0))
        if base_coefficient or gamma_coefficient:
            evaluated_structure.append(
                {
                    "X": left,
                    "Y": right,
                    "Z": result,
                    "coeff": _fraction_string(base_coefficient),
                    "kappa_coeff": _fraction_string(gamma_coefficient),
                    "sign_rule": "graded",
                }
            )

    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n + 1})",
        },
        "source_files": {
            "structure": f"C_{n}_structure.json",
            "gamma": f"C_{n}_gamma.json",
        },
        "gb_assignment": {
            "profile": "checkerboard",
            "rule": "gb[r,c] = (-1)^(r+c), with zero-based row and column indices",
            "shape": [2, 2 * n],
            "row_labels": ["a_1_p", "a_1_m"],
            "column_labels": columns,
            "values": values,
            "parameter_values": assignment,
        },
        "evaluated_gamma_coefficients": evaluated_gamma_records,
        "evaluated_structure_constants": evaluated_structure,
        "metadata": {
            "generated_by": "src/C_evaluated_generator.py",
            "generation_date": generation_date or date.today().isoformat(),
            "references": [
                "Schema 1: C(n+1) oscillator structure",
                "Schema 2: C(n+1) inhomogeneous gamma structure",
            ],
        },
    }


def write_evaluated_schemas(
    data_dir: Path, ranks: tuple[int, ...] = (1, 2, 3)
) -> list[Path]:
    written = []
    for n in ranks:
        structure = json.loads(
            (data_dir / f"C_{n}_structure.json").read_text(encoding="utf-8")
        )
        gamma = json.loads(
            (data_dir / f"C_{n}_gamma.json").read_text(encoding="utf-8")
        )
        evaluated = evaluate_schema(n, structure, gamma)
        path = data_dir / f"C_{n}_evaluated.json"
        path.write_text(
            json.dumps(evaluated, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        written.append(path)
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data",
    )
    parser.add_argument("--ranks", type=int, nargs="+", default=[1, 2, 3])
    arguments = parser.parse_args()
    for path in write_evaluated_schemas(arguments.data_dir, tuple(arguments.ranks)):
        print(path)


if __name__ == "__main__":
    main()
