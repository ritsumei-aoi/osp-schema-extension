"""Compare evaluated C deformations with coboundaries and solve for gb."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import sympy as sp

from C_coboundary import coefficients_for_map
from verify_C_structure import StructureTable

Coordinate = tuple[str, str, str]
SparseVector = dict[Coordinate, Fraction]


def _add_scaled(
    target: SparseVector, source: SparseVector, scale: Fraction
) -> SparseVector:
    for coordinate, coefficient in source.items():
        target[coordinate] = target.get(coordinate, Fraction(0)) + (
            scale * coefficient
        )
        if not target[coordinate]:
            del target[coordinate]
    return target


def _sparse(entries: list[dict]) -> SparseVector:
    result: SparseVector = {}
    for entry in entries:
        coordinate = (entry["X"], entry["Y"], entry["Z"])
        result[coordinate] = result.get(coordinate, Fraction(0)) + Fraction(
            entry["coeff"]
        )
        if not result[coordinate]:
            del result[coordinate]
    return result


def _insert_column_basis(
    basis: dict[Coordinate, SparseVector], vector: SparseVector
) -> SparseVector:
    reduced = dict(vector)
    while reduced:
        pivot = min(reduced)
        if pivot not in basis:
            scale = reduced[pivot]
            basis[pivot] = {
                coordinate: coefficient / scale
                for coordinate, coefficient in reduced.items()
            }
            return {}
        _add_scaled(reduced, basis[pivot], -reduced[pivot])
    return {}


def _reduce_against_basis(
    basis: dict[Coordinate, SparseVector], vector: SparseVector
) -> SparseVector:
    reduced = dict(vector)
    while reduced:
        pivot = min(reduced)
        if pivot not in basis:
            return reduced
        _add_scaled(reduced, basis[pivot], -reduced[pivot])
    return {}


def _kernel_basis(columns: list[SparseVector]) -> list[list[Fraction]]:
    coordinates = sorted(set().union(*(set(column) for column in columns)))
    rows = [
        [column.get(coordinate, Fraction(0)) for column in columns]
        for coordinate in coordinates
    ]
    row_count, column_count = len(rows), len(columns)
    pivot_columns: list[int] = []
    pivot_row = 0
    for column in range(column_count):
        pivot = next(
            (
                row
                for row in range(pivot_row, row_count)
                if rows[row][column]
            ),
            None,
        )
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        scale = rows[pivot_row][column]
        rows[pivot_row] = [value / scale for value in rows[pivot_row]]
        for row in range(row_count):
            if row == pivot_row or not rows[row][column]:
                continue
            scale = rows[row][column]
            rows[row] = [
                value - scale * pivot_value
                for value, pivot_value in zip(rows[row], rows[pivot_row])
            ]
        pivot_columns.append(column)
        pivot_row += 1
        if pivot_row == row_count:
            break

    free_columns = [
        column for column in range(column_count) if column not in pivot_columns
    ]
    result = []
    for free in free_columns:
        vector = [Fraction(0) for _ in range(column_count)]
        vector[free] = Fraction(1)
        for index, pivot in enumerate(pivot_columns):
            vector[pivot] = -rows[index][free]
        result.append(vector)
    return result


def _odd_map_columns(data: dict) -> list[tuple[str, str, SparseVector]]:
    even = data["basis"]["even"]
    odd = data["basis"]["odd"]
    maps = [
        (source, target)
        for source in even
        for target in odd
    ] + [
        (source, target)
        for source in odd
        for target in even
    ]
    result = []
    for source, target in maps:
        entries = coefficients_for_map(data, {source: {target: Fraction(1)}})
        result.append((source, target, _sparse(entries)))
    return result


def _gamma_parameter_columns(gamma_data: dict) -> tuple[list[str], list[SparseVector]]:
    deformation = gamma_data["inhomogeneous_deformation"]
    parameters = [
        value
        for row in deformation["gb_matrix"]["values"]
        for value in row
    ]
    symbols = [sp.Symbol(parameter) for parameter in parameters]
    columns = [SparseVector() for _ in parameters]
    for entry in deformation["gamma_coefficients"]:
        expression = sp.Poly(sp.sympify(entry["coeff"]), *symbols)
        if expression.total_degree() > 1 or expression.coeff_monomial(1):
            raise ValueError("Gamma coefficients must be homogeneous linear in gb")
        for index, symbol in enumerate(symbols):
            coefficient = expression.coeff_monomial(symbol)
            if coefficient:
                if not coefficient.is_Rational:
                    raise ValueError("Gamma coefficients must be rational-linear in gb")
                coordinate = (entry["X"], entry["Y"], entry["Z"])
                columns[index][coordinate] = (
                    columns[index].get(coordinate, Fraction(0))
                    + Fraction(int(coefficient.p), int(coefficient.q))
                )
    return parameters, columns


def _pair_comparison(evaluated: dict, coboundary: dict, names: list[str]) -> dict:
    left = _sparse(evaluated["evaluated_deformation"]["evaluated_coefficients"])
    right = _sparse(coboundary["coboundary"]["coboundary_coefficients"])
    all_pairs = [(x, y) for i, x in enumerate(names) for y in names[i:]]
    equal = []
    different = []
    for x, y in all_pairs:
        left_pair = {
            z: value for (a, b, z), value in left.items() if (a, b) == (x, y)
        }
        right_pair = {
            z: value for (a, b, z), value in right.items() if (a, b) == (x, y)
        }
        (equal if left_pair == right_pair else different).append(
            {
                "X": x,
                "Y": y,
                "gamma": left_pair,
                "delta_f": right_pair,
            }
        )
    return {"equal": equal, "different": different}


def analyze_rank(rank: int, data_dir: Path) -> dict:
    structure = json.loads((data_dir / f"C_{rank}_structure.json").read_text())
    gamma_data = json.loads((data_dir / f"C_{rank}_gamma.json").read_text())
    evaluated = json.loads((data_dir / f"C_{rank}_evaluated.json").read_text())
    coboundary = json.loads((data_dir / f"C_{rank}_coboundary.json").read_text())
    table = StructureTable(structure)
    comparison = _pair_comparison(evaluated, coboundary, table.names)

    coboundary_basis: dict[Coordinate, SparseVector] = {}
    for _, _, vector in _odd_map_columns(structure):
        _insert_column_basis(coboundary_basis, vector)
    parameters, gamma_columns = _gamma_parameter_columns(gamma_data)
    residuals = [
        _reduce_against_basis(coboundary_basis, column)
        for column in gamma_columns
    ]
    kernel = _kernel_basis(residuals)
    conditions = [
        {
            parameter: str(coefficient)
            for parameter, coefficient in zip(parameters, vector)
            if coefficient
        }
        for vector in kernel
    ]
    return {
        "rank": rank,
        "generator_count": len(table.names),
        "pair_comparison": comparison,
        "gb_parameters": parameters,
        "coboundary_dimension": len(coboundary_basis),
        "quotient_rank": len(parameters) - len(kernel),
        "trivial_gb_subspace_dimension": len(kernel),
        "trivial_gb_subspace_basis": conditions,
    }


def _format_vector(vector: dict[str, str]) -> str:
    if not vector:
        return "0"
    return " + ".join(
        f"{coefficient}*{parameter}" for parameter, coefficient in vector.items()
    )


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    for rank in (1, 2, 3):
        report = analyze_rank(rank, root / "data")
        comparison = report["pair_comparison"]
        print(
            f"C_{rank}: fixed all-+1 map comparison: "
            f"{len(comparison['equal'])} equal pairs, "
            f"{len(comparison['different'])} differing pairs"
        )
        for pair in comparison["different"][:2]:
            print(
                f"  ({pair['X']}, {pair['Y']}): "
                f"gamma={pair['gamma']}, delta_f={pair['delta_f']}"
            )
        print(
            f"  general odd-map search: coboundary rank "
            f"{report['coboundary_dimension']}; quotient rank "
            f"{report['quotient_rank']}; allowed gb subspace "
            f"dimension {report['trivial_gb_subspace_dimension']}"
        )
        for vector in report["trivial_gb_subspace_basis"]:
            print(f"  trivial family: {_format_vector(vector)}")
