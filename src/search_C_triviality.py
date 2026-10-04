#!/usr/bin/env python3
"""Compare evaluated C deformations with the exact coboundary image."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path
from typing import TypeAlias


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
Coordinate: TypeAlias = tuple[str, str, str]
Vector: TypeAlias = dict[Coordinate, Fraction]


def _add_scaled(target: Vector, source: Vector, scale: Fraction) -> None:
    for coordinate, coefficient in source.items():
        target[coordinate] = target.get(coordinate, Fraction(0)) + scale * coefficient
        if not target[coordinate]:
            del target[coordinate]


def _reduce(vector: Vector, pivots: dict[Coordinate, Vector]) -> Vector:
    result = dict(vector)
    while result:
        pivot = min(result)
        basis_vector = pivots.get(pivot)
        if basis_vector is None:
            break
        _add_scaled(result, basis_vector, -result[pivot])
    return result


def _extend_basis(vector: Vector, pivots: dict[Coordinate, Vector]) -> bool:
    residual = _reduce(vector, pivots)
    if not residual:
        return False
    pivot = min(residual)
    leading_coefficient = residual[pivot]
    pivots[pivot] = {
        coordinate: coefficient / leading_coefficient
        for coordinate, coefficient in residual.items()
    }
    return True


def _read(data_dir: Path, filename: str) -> dict[str, object]:
    with (data_dir / filename).open(encoding="utf-8") as stream:
        return json.load(stream)


def analyze_rank(rank: int, data_dir: Path = DATA_DIR) -> dict[str, object]:
    structure = _read(data_dir, f"C_{rank}_structure.json")
    gamma = _read(data_dir, f"C_{rank}_gamma.json")
    evaluated = _read(data_dir, f"C_{rank}_evaluated.json")
    coboundary = _read(data_dir, f"C_{rank}_coboundary.json")
    for schema in (structure, gamma, evaluated, coboundary):
        if schema["algebra"]["family"] != "C" or schema["algebra"]["n"] != rank:
            raise ValueError(f"Schema rank mismatch for C_{rank}")

    coboundary_columns: dict[str, Vector] = {
        entry["coefficient"]: {} for entry in coboundary["f"]["map"]
    }
    for entry in coboundary["coboundary"]["entries"]:
        coordinate = entry["X"], entry["Y"], entry["Z"]
        for term in entry["terms"]:
            vector = coboundary_columns[term["phi"]]
            vector[coordinate] = vector.get(coordinate, Fraction(0)) + Fraction(
                term["coeff"]
            )

    image_basis: dict[Coordinate, Vector] = {}
    for vector in coboundary_columns.values():
        _extend_basis(vector, image_basis)

    gamma_columns: dict[str, Vector] = {
        parameter: {}
        for row in gamma["gb_matrix"]["entries"].values()
        for parameter in row.values()
    }
    for entry in gamma["gamma_structure"]:
        coordinate = entry["X"], entry["Y"], entry["Z"]
        vector = gamma_columns[entry["gb"]]
        vector[coordinate] = vector.get(coordinate, Fraction(0)) + Fraction(
            entry["coeff"]
        )

    combined_basis = dict(image_basis)
    for vector in gamma_columns.values():
        _extend_basis(vector, combined_basis)
    quotient_rank = len(combined_basis) - len(image_basis)
    if quotient_rank != len(gamma_columns):
        raise ValueError(
            f"Gamma classes are not independent modulo coboundaries at rank {rank}"
        )

    evaluated_vector: Vector = {}
    for entry in evaluated["structure_constants"]:
        coefficient = Fraction(entry["kappa_coeff"])
        if coefficient:
            coordinate = entry["X"], entry["Y"], entry["Z"]
            evaluated_vector[coordinate] = coefficient
    evaluated_residual = _reduce(evaluated_vector, image_basis)

    kappa_coefficients: dict[Coordinate, dict[str, Fraction]] = {}
    for parameter, vector in gamma_columns.items():
        for coordinate, coefficient in vector.items():
            if coordinate[2] != "K":
                continue
            by_parameter = kappa_coefficients.setdefault(coordinate, {})
            by_parameter[parameter] = by_parameter.get(parameter, Fraction(0)) + coefficient
    witnesses: dict[str, dict[str, object]] = {}
    for coordinate, by_parameter in sorted(kappa_coefficients.items()):
        nonzero = {
            parameter: coefficient
            for parameter, coefficient in by_parameter.items()
            if coefficient
        }
        if len(nonzero) == 1:
            parameter, coefficient = next(iter(nonzero.items()))
            witnesses.setdefault(
                parameter,
                {
                    "X": coordinate[0],
                    "Y": coordinate[1],
                    "Z": coordinate[2],
                    "coeff": str(coefficient),
                },
            )

    if set(witnesses) != set(gamma_columns):
        raise ValueError(f"Not every gb parameter has an isolated K obstruction at rank {rank}")
    return {
        "rank": rank,
        "generator_count": len(structure["parity"]),
        "phi_count": len(coboundary_columns),
        "coboundary_rank": len(image_basis),
        "parameter_count": len(gamma_columns),
        "quotient_rank": quotient_rank,
        "all_plus_residual_count": len(evaluated_residual),
        "all_plus_trivial": not evaluated_residual,
        "isolated_K_witnesses": witnesses,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ranks", type=int, nargs="+", default=[1, 2, 3])
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    arguments = parser.parse_args()
    for rank in arguments.ranks:
        result = analyze_rank(rank, arguments.data_dir)
        status = "TRIVIAL" if result["all_plus_trivial"] else "NON-TRIVIAL"
        print(
            f"C_{rank}: {status}; coboundary image rank "
            f"{result['coboundary_rank']}/{result['phi_count']}, "
            f"gb quotient rank {result['quotient_rank']}/{result['parameter_count']}, "
            f"all-plus residual coordinates {result['all_plus_residual_count']}"
        )
        for parameter, witness in result["isolated_K_witnesses"].items():
            print(
                f"  {parameter}: ({witness['X']}, {witness['Y']}) -> "
                f"{witness['coeff']} K"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
