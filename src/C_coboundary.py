#!/usr/bin/env python3
"""Generate Schema 4 coboundary data for C(n+1)."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import date
from fractions import Fraction
from pathlib import Path
from typing import TypeAlias

SUPPORTED_RANKS = {1, 2, 3}
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

Polynomial: TypeAlias = dict[str, Fraction]
BracketMap: TypeAlias = dict[tuple[str, str], dict[str, Fraction]]
CoboundaryTerms: TypeAlias = dict[tuple[str, str, str], Polynomial]


def _schema1_data(
    schema1: dict[str, object],
) -> tuple[list[str], dict[str, int], BracketMap]:
    basis = schema1.get("basis")
    parity = schema1.get("parity")
    structure_constants = schema1.get("structure_constants")
    if (
        not isinstance(basis, dict)
        or not isinstance(basis.get("even"), list)
        or not isinstance(basis.get("odd"), list)
        or not all(isinstance(label, str) for label in basis["even"] + basis["odd"])
        or not isinstance(parity, dict)
        or not isinstance(structure_constants, list)
    ):
        raise ValueError("Schema 1 has invalid basis, parity, or bracket fields.")

    even = basis["even"]
    odd = basis["odd"]
    labels = odd + even
    if len(labels) != len(set(labels)):
        raise ValueError("Schema 1 basis contains duplicate generator labels.")
    expected_parity = {label: 1 for label in odd} | {label: 0 for label in even}
    if parity != expected_parity:
        raise ValueError("Schema 1 parity map does not match its basis.")

    brackets: BracketMap = defaultdict(dict)
    for record in structure_constants:
        if not isinstance(record, dict):
            raise ValueError("Schema 1 structure-constant records must be objects.")
        try:
            left, right, output = record["X"], record["Y"], record["Z"]
            coefficient, sign_rule = record["coeff"], record["sign_rule"]
        except KeyError as error:
            raise ValueError("Schema 1 structure-constant record is incomplete.") from error
        if (
            not all(isinstance(label, str) for label in (left, right, output))
            or left not in parity
            or right not in parity
            or output not in parity
            or sign_rule != "graded"
            or not isinstance(coefficient, str)
        ):
            raise ValueError(f"Invalid Schema 1 structure-constant record: {record!r}.")
        try:
            value = Fraction(coefficient)
        except (ValueError, ZeroDivisionError) as error:
            raise ValueError(f"Invalid rational coefficient {coefficient!r}.") from error
        if not value:
            raise ValueError("Schema 1 structure constants must be nonzero.")
        pair = (left, right)
        if output in brackets[pair]:
            raise ValueError(f"Duplicate Schema 1 structure constant for {pair}, {output}.")
        brackets[pair][output] = value
    return labels, expected_parity, brackets


def _build_odd_map(
    labels: list[str],
    parity: dict[str, int],
) -> tuple[dict[str, list[tuple[str, str]]], list[dict[str, str]], list[str]]:
    map_terms: dict[str, list[tuple[str, str]]] = {}
    entries: list[dict[str, str]] = []
    parameter_order: list[str] = []
    for input_label in labels:
        outputs = []
        for output_label in labels:
            if parity[output_label] == parity[input_label]:
                continue
            parameter = f"phi_{output_label}_from_{input_label}"
            outputs.append((output_label, parameter))
            parameter_order.append(parameter)
            entries.append(
                {
                    "input": input_label,
                    "output": output_label,
                    "parameter": parameter,
                }
            )
        map_terms[input_label] = outputs
    return map_terms, entries, parameter_order


def _add_scaled(
    target: Polynomial,
    source: Polynomial,
    scale: Fraction,
) -> None:
    for parameter, coefficient in source.items():
        value = target.get(parameter, Fraction(0)) + scale * coefficient
        if value:
            target[parameter] = value
        else:
            target.pop(parameter, None)


def _format_polynomial(
    polynomial: Polynomial,
    parameter_order: list[str],
) -> str:
    pieces: list[str] = []
    for parameter in parameter_order:
        coefficient = polynomial.get(parameter, Fraction(0))
        if not coefficient:
            continue
        if coefficient == 1:
            pieces.append(parameter)
        elif coefficient == -1:
            pieces.append(f"-{parameter}")
        else:
            pieces.append(f"{coefficient}*{parameter}")
    if not pieces:
        raise ValueError("Cannot serialize a zero coboundary coefficient.")
    return " + ".join(pieces).replace("+ -", "- ")


def _compute_coboundary_terms(
    labels: list[str],
    parity: dict[str, int],
    brackets: BracketMap,
    map_terms: dict[str, list[tuple[str, str]]],
) -> CoboundaryTerms:
    terms: CoboundaryTerms = defaultdict(dict)
    for left in labels:
        for right in labels:
            first_scale = Fraction(-1 if parity[left] else 1)
            second_exponent = (parity[left] + 1) * parity[right]
            second_scale = Fraction(-1 if second_exponent % 2 == 0 else 1)

            for map_output, parameter in map_terms[right]:
                for output, coefficient in brackets.get((left, map_output), {}).items():
                    _add_scaled(
                        terms[(left, right, output)],
                        {parameter: coefficient},
                        first_scale,
                    )
            for map_output, parameter in map_terms[left]:
                for output, coefficient in brackets.get((right, map_output), {}).items():
                    _add_scaled(
                        terms[(left, right, output)],
                        {parameter: coefficient},
                        second_scale,
                    )
            for bracket_output, coefficient in brackets.get((left, right), {}).items():
                for output, parameter in map_terms[bracket_output]:
                    _add_scaled(
                        terms[(left, right, output)],
                        {parameter: coefficient},
                        Fraction(-1),
                    )

    for left in labels:
        for right in labels:
            sign = Fraction(-1 if parity[left] * parity[right] % 2 == 0 else 1)
            for output in labels:
                forward = terms.get((left, right, output), {})
                reverse = terms.get((right, left, output), {})
                expected: Polynomial = {}
                _add_scaled(expected, forward, sign)
                if reverse != expected:
                    raise ValueError(
                        f"Computed coboundary violates graded skew-symmetry for "
                        f"({left}, {right}, {output})."
                    )
                if forward and parity[output] != (parity[left] ^ parity[right] ^ 1):
                    raise ValueError(
                        f"Computed coboundary has incorrect parity for "
                        f"({left}, {right}, {output})."
                    )
    return terms


def compute_coboundary_coefficients(
    schema1: dict[str, object],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Compute δf for a general odd endomorphism of the Schema 1 basis."""
    labels, parity, brackets = _schema1_data(schema1)
    map_terms, map_entries, parameter_order = _build_odd_map(labels, parity)
    terms = _compute_coboundary_terms(labels, parity, brackets, map_terms)
    records = []
    for left in labels:
        for right in labels:
            for output in labels:
                polynomial = terms.get((left, right, output), {})
                if polynomial:
                    records.append(
                        {
                            "X": left,
                            "Y": right,
                            "Z": output,
                            "coeff": _format_polynomial(polynomial, parameter_order),
                            "sign_rule": "graded",
                        }
                    )
    return map_entries, records


def _central_gamma_components(
    n: int,
    schema1: dict[str, object],
    evaluated_schema: dict[str, object],
) -> list[dict[str, str]]:
    try:
        deformation = evaluated_schema["inhomogeneous_deformation"]
        profile = deformation["evaluation_profile"]
        records = deformation["evaluated_gamma_coefficients"]
        basis = schema1["basis"]
    except (KeyError, TypeError) as error:
        raise ValueError("Schema 3 is missing required evaluated deformation data.") from error
    if (
        not isinstance(deformation, dict)
        or not isinstance(profile, dict)
        or not isinstance(records, list)
        or not isinstance(basis, dict)
        or not isinstance(basis.get("even"), list)
        or not isinstance(basis.get("odd"), list)
    ):
        raise ValueError("Schema 3 has invalid evaluated deformation field types.")
    matrix = deformation.get("gb_matrix")
    parameter_values = profile.get("parameter_values")
    if not isinstance(matrix, dict) or not isinstance(matrix.get("entries"), list):
        raise ValueError("Schema 3 gb_matrix is missing or invalid.")
    if not isinstance(parameter_values, dict):
        raise ValueError("Schema 3 evaluation profile has invalid parameter values.")
    matrix_parameters = [
        parameter
        for row in matrix["entries"]
        if isinstance(row, list)
        for parameter in row
    ]
    if (
        len(matrix_parameters) != 4 * n
        or not all(isinstance(parameter, str) for parameter in matrix_parameters)
        or len(set(matrix_parameters)) != 4 * n
        or set(parameter_values) != set(matrix_parameters)
        or any(type(value) is not int or value != 1 for value in parameter_values.values())
    ):
        raise ValueError("Schema 3 does not use the approved all-positive gb profile.")
    if (
        evaluated_schema.get("algebra") != schema1.get("algebra")
        or evaluated_schema.get("basis") != schema1.get("basis")
        or evaluated_schema.get("parity") != schema1.get("parity")
        or evaluated_schema.get("structure_constants")
        != schema1.get("structure_constants")
        or schema1["algebra"]["n"] != n
        or profile.get("name") != "all_positive"
    ):
        raise ValueError(f"Schema 3 is inconsistent with Schema 1 for n={n}.")
    basis_labels = set(basis["even"] + basis["odd"])
    central_records = []
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("Schema 3 evaluated gamma records must be objects.")
        try:
            left, right, output = record["X"], record["Y"], record["Z"]
            coefficient, sign_rule = record["coeff"], record["sign_rule"]
        except KeyError as error:
            raise ValueError("Schema 3 evaluated gamma record is incomplete.") from error
        if (
            not all(isinstance(label, str) for label in (left, right, output))
            or left not in basis_labels
            or right not in basis_labels
            or output not in basis_labels | {"K"}
            or not isinstance(coefficient, str)
            or sign_rule != "graded"
        ):
            raise ValueError(f"Invalid Schema 3 evaluated gamma record: {record!r}.")
        try:
            value = Fraction(coefficient)
        except (ValueError, ZeroDivisionError) as error:
            raise ValueError(f"Invalid evaluated gamma coefficient {coefficient!r}.") from error
        if not value:
            raise ValueError("Schema 3 evaluated gamma records must be nonzero.")
        if output == "K":
            central_records.append(dict(record))
    return central_records


def build_coboundary_schema(
    n: int,
    data_dir: Path | None = None,
    generation_date: str | None = None,
) -> dict[str, object]:
    if n not in SUPPORTED_RANKS:
        raise ValueError("This generator supports bosonic ranks n=1, 2, and 3.")
    root = data_dir or DATA_DIR
    schema1_path = root / f"C_{n}_structure.json"
    evaluated_path = root / f"C_{n}_evaluated.json"
    schema1 = json.loads(schema1_path.read_text(encoding="utf-8"))
    evaluated_schema = json.loads(evaluated_path.read_text(encoding="utf-8"))
    map_entries, coboundary_records = compute_coboundary_coefficients(schema1)
    central_records = _central_gamma_components(n, schema1, evaluated_schema)

    result = dict(schema1)
    result["coboundary"] = {
        "odd_linear_map": {
            "parity": 1,
            "formula": "f(X) = sum_Y phi_{Y_from_X} Y, with p(Y) = p(X) XOR 1.",
            "normalization": "One independent symbolic coefficient per parity-reversing matrix entry; no global multiplier.",
            "entries": map_entries,
        },
        "delta_f_coefficients": coboundary_records,
        "comparison": {
            "target_file": f"data/C_{n}_evaluated.json",
            "central_output_label": "K",
            "unmatched_central_components": central_records,
            "central_component_note": (
                "delta f maps g tensor g to g for f: g -> g, so these K outputs "
                "from the evaluated deformation cannot be produced by delta f."
            ),
        },
    }
    result["metadata"] = {
        "generated_by": "C_coboundary.py",
        "generation_date": generation_date or date.today().isoformat(),
        "references": [
            f"data/C_{n}_structure.json",
            f"data/C_{n}_evaluated.json",
            "docs/math/C_coboundary_definition.md",
        ],
    }
    return result


def output_path(n: int, data_dir: Path | None = None) -> Path:
    if n not in SUPPORTED_RANKS:
        raise ValueError("This generator supports bosonic ranks n=1, 2, and 3.")
    return (data_dir or DATA_DIR) / f"C_{n}_coboundary.json"


def write_coboundary_schema(n: int, data_dir: Path | None = None) -> Path:
    schema = build_coboundary_schema(n, data_dir)
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
        print(write_coboundary_schema(rank, args.data_dir))


if __name__ == "__main__":
    main()
