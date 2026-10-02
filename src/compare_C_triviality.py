#!/usr/bin/env python3
"""Compare C-family gamma data with the image of the odd coboundary map."""

from __future__ import annotations

import argparse
import json
import re
from fractions import Fraction
from pathlib import Path


Coordinate = tuple[str, str, str]
LinearForm = dict[str, Fraction]
SparseRow = dict[int, Fraction]


def _parse_linear_expression(expression: str, prefix: str) -> LinearForm:
    terms: LinearForm = {}
    normalized = expression.replace(" - ", " + -")
    for token in normalized.split(" + "):
        token = token.strip()
        if not token:
            continue
        sign = Fraction(1)
        if token.startswith("-"):
            sign = Fraction(-1)
            token = token[1:]
        if "*" in token:
            scalar_text, symbol = token.split("*", 1)
            scalar = Fraction(scalar_text)
        else:
            scalar, symbol = Fraction(1), token
        if not re.fullmatch(rf"{re.escape(prefix)}[A-Za-z0-9_]+", symbol):
            raise ValueError(f"Invalid {prefix} expression: {expression}")
        terms[symbol] = terms.get(symbol, Fraction()) + sign * scalar
    return {symbol: value for symbol, value in terms.items() if value}


def _accumulate(target: dict, source: dict, factor: Fraction) -> None:
    for key, value in source.items():
        target[key] = target.get(key, Fraction()) + factor * value
        if not target[key]:
            del target[key]


def _reduce_equations(
    rows: list[tuple[Coordinate, SparseRow, LinearForm]],
    variable_count: int,
) -> tuple[list[LinearForm], list[tuple[LinearForm, dict[Coordinate, Fraction]]]]:
    pivots: dict[int, tuple[SparseRow, LinearForm, dict[Coordinate, Fraction]]] = {}
    constraints: list[tuple[LinearForm, dict[Coordinate, Fraction]]] = []

    for coordinate, raw_coefficients, raw_rhs in rows:
        coefficients = dict(raw_coefficients)
        rhs = dict(raw_rhs)
        provenance = {coordinate: Fraction(1)}
        while coefficients:
            pivot = min(coefficients)
            if pivot >= variable_count:
                raise ValueError("Coboundary matrix column index is out of range")
            if pivot not in pivots:
                scale = coefficients[pivot]
                coefficients = {key: value / scale for key, value in coefficients.items()}
                rhs = {key: value / scale for key, value in rhs.items()}
                provenance = {
                    key: value / scale for key, value in provenance.items()
                }
                pivots[pivot] = (coefficients, rhs, provenance)
                break
            pivot_coefficients, pivot_rhs, pivot_provenance = pivots[pivot]
            factor = coefficients[pivot]
            _accumulate(coefficients, pivot_coefficients, -factor)
            _accumulate(rhs, pivot_rhs, -factor)
            _accumulate(provenance, pivot_provenance, -factor)
        else:
            if rhs:
                constraints.append((rhs, provenance))

    return _independent_constraints(constraints), constraints


def _independent_constraints(
    constraints: list[tuple[LinearForm, dict[Coordinate, Fraction]]]
) -> list[LinearForm]:
    symbols = sorted({symbol for form, _ in constraints for symbol in form})
    pivots: dict[int, list[Fraction]] = {}
    for form, _ in constraints:
        row = [form.get(symbol, Fraction()) for symbol in symbols]
        for column in range(len(symbols)):
            if not row[column]:
                continue
            if column in pivots:
                factor = row[column]
                row = [
                    value - factor * pivot_value
                    for value, pivot_value in zip(row, pivots[column])
                ]
                continue
            scale = row[column]
            row = [value / scale for value in row]
            for other_column, pivot in list(pivots.items()):
                if row[other_column]:
                    factor = row[other_column]
                    pivots[other_column] = [
                        value - factor * new_value
                        for value, new_value in zip(pivot, row)
                    ]
            pivots[column] = row
            break
    result = []
    for row in pivots.values():
        result.append({
            symbol: value
            for symbol, value in zip(symbols, row)
            if value
        })
    return result


def _format_equation(form: LinearForm) -> str:
    pieces: list[str] = []
    for symbol in sorted(form):
        value = form[symbol]
        magnitude = abs(value)
        term = symbol if magnitude == 1 else f"{magnitude}*{symbol}"
        if not pieces:
            pieces.append(("-" if value < 0 else "") + term)
        else:
            pieces.append(f" {'-' if value < 0 else '+'} {term}")
    return " = 0" if not pieces else "".join(pieces) + " = 0"


def analyze_triviality(
    structure: dict, gamma: dict, coboundary: dict
) -> dict:
    rank = structure["algebra"]["n"]
    if gamma["algebra"]["n"] != rank or coboundary["algebra"]["n"] != rank:
        raise ValueError("Input schemas have inconsistent ranks")
    if (
        gamma["source_schema"] != f"C_{rank}_structure.json"
        or coboundary["source_schema"] != f"C_{rank}_structure.json"
    ):
        raise ValueError("Gamma or coboundary data references another structure schema")

    map_parameters = [
        entry["coefficient"]
        for entry in coboundary["odd_linear_map"]["entries"]
    ]
    gb_parameters = [
        parameter
        for row in gamma["gb_matrix"]["entries"]
        for parameter in row
    ]
    map_index = {parameter: index for index, parameter in enumerate(map_parameters)}

    delta_by_coordinate: dict[Coordinate, SparseRow] = {}
    for entry in coboundary["coboundary"]["coefficients"]:
        coordinate = (entry["X"], entry["Y"], entry["Z"])
        parsed = _parse_linear_expression(entry["coeff"], "phi_")
        delta_by_coordinate[coordinate] = {
            map_index[parameter]: coefficient
            for parameter, coefficient in parsed.items()
        }

    gamma_by_coordinate: dict[Coordinate, LinearForm] = {}
    for entry in gamma["inhomogeneous_deformation"]["gamma_coefficients"]:
        coordinate = (entry["X"], entry["Y"], entry["Z"])
        parsed = _parse_linear_expression(entry["coeff"], "gb_")
        gamma_by_coordinate[coordinate] = parsed
    central_witnesses: dict[str, dict] = {}
    for entry in gamma["inhomogeneous_deformation"]["gamma_coefficients"]:
        if entry["Z"] != "K":
            continue
        for parameter, coefficient in _parse_linear_expression(
            entry["coeff"], "gb_"
        ).items():
            if coefficient and parameter not in central_witnesses:
                central_witnesses[parameter] = {
                    "X": entry["X"],
                    "Y": entry["Y"],
                    "coefficient": str(coefficient),
                }
    if set(central_witnesses) != set(gb_parameters):
        missing = sorted(set(gb_parameters) - set(central_witnesses))
        raise ValueError(f"Some gb parameters lack a central obstruction: {missing}")

    coordinates = sorted(set(delta_by_coordinate) | set(gamma_by_coordinate))
    rows = [
        (
            coordinate,
            delta_by_coordinate.get(coordinate, {}),
            gamma_by_coordinate.get(coordinate, {}),
        )
        for coordinate in coordinates
    ]
    equations, certificates = _reduce_equations(rows, len(map_parameters))
    full_rank = len(gb_parameters)
    all_plus_obstructions = [
        form for form, _ in certificates if sum(form.values(), Fraction()) != 0
    ]

    failed_rows: list[dict] = []
    if all_plus_obstructions:
        witness_form, provenance = next(
            (form, origin) for form, origin in certificates
            if sum(form.values(), Fraction()) != 0
        )
        for coordinate, factor in sorted(provenance.items())[:8]:
            gamma_value = sum(
                gamma_by_coordinate.get(coordinate, {}).values(), Fraction()
            )
            failed_rows.append({
                "X": coordinate[0],
                "Y": coordinate[1],
                "Z": coordinate[2],
                "combination_coefficient": str(factor),
                "all_plus_gamma_coefficient": str(gamma_value),
            })
    return {
        "rank": rank,
        "gb_parameters": gb_parameters,
        "coboundary_parameters": map_parameters,
        "coordinate_count": len(coordinates),
        "constraint_rank": len(equations),
        "trivial_parameter_dimension": full_rank - len(equations),
        "necessary_sufficient_conditions": [
            _format_equation(form) for form in equations
        ],
        "central_witnesses": central_witnesses,
        "all_plus_trivial": not all_plus_obstructions,
        "all_plus_obstruction": (
            _format_equation(witness_form) if all_plus_obstructions else None
        ),
        "all_plus_witness_coordinates": failed_rows,
    }


def _load(data_dir: Path, rank: int, suffix: str) -> dict:
    path = data_dir / f"C_{rank}_{suffix}.json"
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--ranks", type=int, nargs="+", default=[1, 2, 3])
    args = parser.parse_args()
    for rank in args.ranks:
        result = analyze_triviality(
            _load(args.data_dir, rank, "structure"),
            _load(args.data_dir, rank, "gamma"),
            _load(args.data_dir, rank, "coboundary"),
        )
        print(
            f"C_{rank}: all_plus_trivial={result['all_plus_trivial']}; "
            f"trivial gb dimension={result['trivial_parameter_dimension']}/"
            f"{len(result['gb_parameters'])}"
        )
        for condition in result["necessary_sufficient_conditions"]:
            print(f"  condition: {condition}")
        if result["all_plus_obstruction"]:
            print(f"  all-plus obstruction: {result['all_plus_obstruction']}")
            for coordinate in result["all_plus_witness_coordinates"]:
                print(
                    "  witness: "
                    f"({coordinate['X']}, {coordinate['Y']}, {coordinate['Z']}), "
                    f"combination={coordinate['combination_coefficient']}, "
                    f"gamma(all +1)={coordinate['all_plus_gamma_coefficient']}"
                )


if __name__ == "__main__":
    main()
