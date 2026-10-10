#!/usr/bin/env python3
"""Generate and verify uniform-positive Schema 3 data for C(n+1)."""

from __future__ import annotations

import argparse
import json
from datetime import date
from fractions import Fraction
from pathlib import Path
from typing import Iterable

from C_generators import build_basis
from C_gamma import _load_structure, verify_gamma_schema


PROFILE = "uniform_positive"


def _format_fraction(value: Fraction) -> str:
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


def _parameter_assignment(gamma_data: dict[str, object]) -> dict[str, object]:
    try:
        matrix = gamma_data["inhomogeneous_deformation"]["gb_matrix"]
        entries = matrix["entries"]
    except (KeyError, TypeError) as exc:
        raise ValueError("Schema 2 is missing its gb parameter matrix") from exc
    if not isinstance(entries, list) or any(
        not isinstance(row, list) for row in entries
    ):
        raise ValueError("Schema 2 gb_matrix entries must be a matrix")
    parameters = [parameter for row in entries for parameter in row]
    if (
        not parameters
        or any(not isinstance(parameter, str) for parameter in parameters)
        or len(parameters) != len(set(parameters))
    ):
        raise ValueError("Schema 2 gb_matrix contains invalid parameter labels")
    return {
        "profile": PROFILE,
        "description": "All scalar gb parameters are set to +1.",
        "parameters": {parameter: "1" for parameter in parameters},
    }


def _evaluate_constants(
    gamma_data: dict[str, object], assignment: dict[str, object]
) -> list[dict[str, object]]:
    records = gamma_data.get("gamma_constants")
    if not isinstance(records, list):
        raise ValueError("Schema 2 gamma_constants must be a list")
    values = assignment["parameters"]
    if not isinstance(values, dict):
        raise ValueError("gb assignment parameters must be an object")

    evaluated: dict[tuple[str, str, str], Fraction] = {}
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError(f"gamma_constants[{index}] must be an object")
        try:
            key = (record["X"], record["Y"], record["Z"])
            terms = record["coeff"]
            if record["sign_rule"] != "graded" or not isinstance(terms, list):
                raise ValueError
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"Invalid Schema 2 gamma_constants[{index}]") from exc
        for term in terms:
            try:
                parameter = term["parameter"]
                scalar = Fraction(term["scalar"])
                value = Fraction(values[parameter])
            except (KeyError, TypeError, ValueError, ZeroDivisionError) as exc:
                raise ValueError(
                    f"Invalid coefficient in Schema 2 gamma_constants[{index}]"
                ) from exc
            evaluated[key] = evaluated.get(key, Fraction()) + scalar * value

    return [
        {
            "X": left,
            "Y": right,
            "Z": output,
            "coeff": _format_fraction(coefficient),
            "sign_rule": "graded",
        }
        for (left, right, output), coefficient in evaluated.items()
        if coefficient
    ]


def build_evaluated_schema(
    gamma_data: dict[str, object], generation_date: str | None = None
) -> dict[str, object]:
    if gamma_data.get("schema_layer") != 2:
        raise ValueError("Input must be Schema 2 (schema_layer = 2)")
    if generation_date is None:
        generation_date = date.today().isoformat()
    try:
        parsed_date = date.fromisoformat(generation_date)
    except (TypeError, ValueError) as exc:
        raise ValueError("generation_date must use YYYY-MM-DD format") from exc
    if parsed_date.isoformat() != generation_date:
        raise ValueError("generation_date must use YYYY-MM-DD format")

    assignment = _parameter_assignment(gamma_data)
    try:
        metadata = gamma_data["metadata"]
        references = metadata["references"]
        rank = gamma_data["algebra"]["n"]
    except (KeyError, TypeError) as exc:
        raise ValueError("Schema 2 is missing required context or metadata") from exc

    return {
        "schema_version": gamma_data["schema_version"],
        "schema_layer": 3,
        "schema_type": "evaluated_structure",
        "algebra": gamma_data["algebra"],
        "basis": gamma_data["basis"],
        "parity": gamma_data["parity"],
        "central_elements": gamma_data["central_elements"],
        "scalar_output": gamma_data["scalar_output"],
        "gb_assignment": assignment,
        "evaluated_constants": _evaluate_constants(gamma_data, assignment),
        "metadata": {
            "generated_by": "C_evaluate.py",
            "generation_date": generation_date,
            "source_schema": f"C_{rank}_gamma.json",
            "gb_profile": PROFILE,
            "references": references,
        },
    }


def verify_evaluated_schema(
    gamma_data: dict[str, object], evaluated_data: dict[str, object]
) -> int:
    try:
        generation_date = evaluated_data["metadata"]["generation_date"]
    except (KeyError, TypeError) as exc:
        raise ValueError("Schema 3 metadata is missing its generation date") from exc
    expected = build_evaluated_schema(gamma_data, generation_date)
    if evaluated_data != expected:
        raise ValueError("Schema 3 data does not match evaluation of Schema 2")
    return len(expected["evaluated_constants"])


def generate_files(
    ranks: Iterable[int], data_dir: Path, generation_date: str | None = None
) -> list[tuple[Path, int, int]]:
    prepared: list[tuple[Path, dict[str, object], dict[str, object], int]] = []
    seen_ranks: set[int] = set()
    for n in ranks:
        if not isinstance(n, int) or isinstance(n, bool) or n < 1:
            raise ValueError(f"Invalid bosonic rank: {n!r}")
        if n in seen_ranks:
            raise ValueError(f"Duplicate bosonic rank: {n}")
        seen_ranks.add(n)

        basis = build_basis(n)
        structure_path = data_dir / f"C_{n}_structure.json"
        gamma_path = data_dir / f"C_{n}_gamma.json"
        if not structure_path.is_file():
            raise FileNotFoundError(f"Schema 1 file does not exist: {structure_path}")
        if not gamma_path.is_file():
            raise FileNotFoundError(f"Schema 2 file does not exist: {gamma_path}")
        structure_data = _load_structure(structure_path, basis)
        gamma_data = json.loads(gamma_path.read_text(encoding="utf-8"))
        checked_pairs, _ = verify_gamma_schema(basis, structure_data, gamma_data)
        evaluated_data = build_evaluated_schema(gamma_data, generation_date)
        verify_evaluated_schema(gamma_data, evaluated_data)
        prepared.append(
            (
                data_dir / f"C_{n}_evaluated.json",
                gamma_data,
                evaluated_data,
                checked_pairs,
            )
        )

    generated: list[tuple[Path, int, int]] = []
    for destination, gamma_data, evaluated_data, checked_pairs in prepared:
        destination.write_text(
            json.dumps(evaluated_data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        persisted = json.loads(destination.read_text(encoding="utf-8"))
        evaluated_count = verify_evaluated_schema(gamma_data, persisted)
        generated.append((destination, checked_pairs, evaluated_count))
    return generated


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ranks",
        type=int,
        nargs="+",
        default=[1, 2, 3],
        help="Bosonic ranks to generate (default: 1 2 3)",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data",
        help="Directory containing Schema 1/2 files and receiving Schema 3 files",
    )
    arguments = parser.parse_args()
    for path, pair_count, constant_count in generate_files(
        arguments.ranks, arguments.data_dir
    ):
        print(
            f"{path}: verified {pair_count} Schema 1 ordered pairs and "
            f"{constant_count} evaluated constants"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
