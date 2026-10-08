"""Compare evaluated C(n+1) deformations with the odd coboundary image."""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path

from src.C_generators import ROOT

Row = tuple[str, str, str]
Vector = dict[Row, Fraction]


def _add_scaled(target: dict, source: dict, scale: Fraction) -> None:
    for key, coefficient in source.items():
        target[key] = target.get(key, Fraction(0)) + scale * coefficient
        if not target[key]:
            del target[key]


def _read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc


def _span_solver(columns: dict[str, Vector]):
    pivots: list[tuple[Row, Vector, dict[str, Fraction]]] = []
    pivot_rows: set[Row] = set()
    for variable, original in columns.items():
        vector = dict(original)
        expression = {variable: Fraction(1)}
        for pivot, pivot_vector, pivot_expression in pivots:
            factor = vector.get(pivot, Fraction(0))
            if factor:
                _add_scaled(vector, pivot_vector, -factor)
                _add_scaled(expression, pivot_expression, -factor)
        candidates = sorted(set(vector) - pivot_rows)
        if not candidates:
            continue
        pivot = candidates[0]
        scale = vector[pivot]
        vector = {row: value / scale for row, value in vector.items()}
        expression = {name: value / scale for name, value in expression.items()}
        pivots.append((pivot, vector, expression))
        pivot_rows.add(pivot)

    def reduce(target: Vector) -> tuple[dict[str, Fraction], Vector]:
        vector = dict(target)
        expression: dict[str, Fraction] = {}
        for pivot, pivot_vector, pivot_expression in pivots:
            factor = vector.get(pivot, Fraction(0))
            if factor:
                _add_scaled(vector, pivot_vector, -factor)
                _add_scaled(expression, pivot_expression, factor)
        return expression, vector

    return pivots, reduce


def _independent_conditions(residuals: dict[str, Vector], parameters: list[str]):
    parameter_order = {name: index for index, name in enumerate(parameters)}
    raw_rows: dict[Row, dict[int, Fraction]] = {}
    for parameter, residual in residuals.items():
        for row, coefficient in residual.items():
            raw_rows.setdefault(row, {})[parameter_order[parameter]] = coefficient

    pivots: list[tuple[int, dict[int, Fraction]]] = []
    for original in raw_rows.values():
        equation = dict(original)
        for pivot, pivot_equation in pivots:
            factor = equation.get(pivot, Fraction(0))
            if factor:
                _add_scaled(equation, pivot_equation, -factor)
        nonzero = sorted(equation)
        if not nonzero:
            continue
        pivot = nonzero[0]
        scale = equation[pivot]
        equation = {index: value / scale for index, value in equation.items()}
        pivots.append((pivot, equation))
    return pivots


def _null_vector(pivots: list[tuple[int, dict[int, Fraction]]], width: int):
    pivot_columns = {pivot for pivot, _ in pivots}
    free_columns = [index for index in range(width) if index not in pivot_columns]
    if not free_columns:
        return None
    vector = {index: Fraction(0) for index in range(width)}
    vector[free_columns[0]] = Fraction(1)
    for pivot, equation in reversed(pivots):
        vector[pivot] = -sum(
            coefficient * vector[index]
            for index, coefficient in equation.items()
            if index != pivot
        )
    return {index: value for index, value in vector.items() if value}


def analyze_rank(n: int) -> dict:
    if n < 1:
        raise ValueError("Bosonic rank n must be at least 1")
    structure = _read_json(ROOT / "data" / f"C_{n}_structure.json")
    gamma = _read_json(ROOT / "data" / f"C_{n}_gamma.json")
    evaluated = _read_json(ROOT / "data" / f"C_{n}_evaluated.json")
    coboundary = _read_json(ROOT / "data" / f"C_{n}_coboundary.json")
    expected_sources = (
        (gamma.get("source_schema"), f"C_{n}_structure.json"),
        (evaluated.get("source_structure_schema"), f"C_{n}_structure.json"),
        (evaluated.get("source_gamma_schema"), f"C_{n}_gamma.json"),
        (coboundary.get("source_structure_schema"), f"C_{n}_structure.json"),
    )
    if any(actual != expected for actual, expected in expected_sources):
        raise ValueError(f"Layer source mismatch for n={n}")

    columns: dict[str, Vector] = {}
    for entry in coboundary["coboundary_coefficients"]:
        row = (entry["X"], entry["Y"], entry["Z"])
        vector = columns.setdefault(entry["phi"], {})
        vector[row] = vector.get(row, Fraction(0)) + Fraction(entry["coeff"])
    _, reduce = _span_solver(columns)

    parameters = [entry["label"] for entry in gamma["gb_matrix"]["parameters"]]
    parameter_vectors: dict[str, Vector] = {parameter: {} for parameter in parameters}
    gamma_entries = gamma["inhomogeneous_deformation"]["gamma_coefficients"]
    for entry in gamma_entries:
        row = (entry["X"], entry["Y"], entry["Z"])
        parameter = entry["parameter"]
        if parameter not in parameter_vectors:
            raise ValueError(f"unknown gb parameter {parameter!r} in gamma schema")
        vector = parameter_vectors[parameter]
        vector[row] = vector.get(row, Fraction(0)) + Fraction(entry["coeff"])
    parameter_vectors = {
        parameter: {row: value for row, value in vector.items() if value}
        for parameter, vector in parameter_vectors.items()
    }

    residuals = {
        parameter: reduce(vector)[1]
        for parameter, vector in parameter_vectors.items()
    }
    conditions = _independent_conditions(residuals, parameters)
    scalar_witnesses = []
    for parameter in gamma["gb_matrix"]["parameters"]:
        fermion_sign = parameter["fermion"].rsplit("_", 1)[1]
        boson_index, boson_sign = parameter["boson"][2:].split("_")
        root_suffix = fermion_sign + ("m" if boson_sign == "p" else "p")
        witness_pair = (
            f"E_eps1_del{boson_index}_{root_suffix}",
            f"E_2del{boson_index}_{boson_sign}",
            "K",
        )
        terms = [
            entry for entry in gamma_entries
            if (entry["X"], entry["Y"], entry["Z"]) == witness_pair
        ]
        expected_coefficient = "-1" if boson_sign == "p" else "1"
        if len(terms) != 1 or terms[0]["parameter"] != parameter["label"] or terms[0]["coeff"] != expected_coefficient:
            raise ValueError(
                f"expected unique scalar obstruction for {parameter['label']} at {witness_pair}"
            )
        scalar_witnesses.append({
            "parameter": parameter["label"],
            "X": witness_pair[0],
            "Y": witness_pair[1],
            "Z": "K",
            "coeff": expected_coefficient,
        })
    all_positive = {
        row: sum(vector.get(row, Fraction(0)) for vector in parameter_vectors.values())
        for row in set().union(*(vector.keys() for vector in parameter_vectors.values()))
    }
    all_positive = {row: value for row, value in all_positive.items() if value}
    _, all_positive_residual = reduce(all_positive)
    null_vector = _null_vector(conditions, len(parameters))
    trivial_profile = None
    if null_vector:
        trivial_profile = {
            parameters[index]: value
            for index, value in null_vector.items()
        }

    evaluated_vector = {
        (entry["X"], entry["Y"], entry["Z"]): Fraction(entry["coefficients"]["kappa"])
        for entry in evaluated["evaluated_structure_constants"]
        if Fraction(entry["coefficients"]["kappa"])
    }
    if evaluated_vector != all_positive:
        raise ValueError(f"Schema 3 gamma component does not match all-positive Schema 2 data for n={n}")

    base_vector = {
        (entry["X"], entry["Y"], entry["Z"]): Fraction(entry["coeff"])
        for entry in structure["structure_constants"]
    }
    evaluated_base = {
        (entry["X"], entry["Y"], entry["Z"]): Fraction(entry["coefficients"]["constant"])
        for entry in evaluated["evaluated_structure_constants"]
        if Fraction(entry["coefficients"]["constant"])
    }
    if base_vector != evaluated_base:
        raise ValueError(f"Schema 3 constant part does not match Schema 1 for n={n}")

    return {
        "n": n,
        "parameters": parameters,
        "coboundary_variables": len(columns),
        "coboundary_rank": len(_span_solver(columns)[0]),
        "independent_conditions": conditions,
        "scalar_witnesses": scalar_witnesses,
        "all_positive_residual": all_positive_residual,
        "trivial_profile": trivial_profile,
        "trivial_profile_residual": (
            reduce({
                row: sum(
                    value * parameter_vectors[parameter].get(row, Fraction(0))
                    for parameter, value in trivial_profile.items()
                )
                for row in set().union(*(vector.keys() for vector in parameter_vectors.values()))
            })[1]
            if trivial_profile else None
        ),
        "parameter_vectors": parameter_vectors,
    }


def _format_equation(equation: dict[int, Fraction], parameters: list[str]) -> str:
    terms = []
    for index, coefficient in sorted(equation.items()):
        magnitude = str(abs(coefficient))
        term = parameters[index] if magnitude == "1" else f"{magnitude}*{parameters[index]}"
        if not terms:
            terms.append(f"-{term}" if coefficient < 0 else term)
        else:
            terms.append(f" - {term}" if coefficient < 0 else f" + {term}")
    return "".join(terms) + " = 0"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ranks", type=int, nargs="+", default=[1, 2, 3])
    args = parser.parse_args()
    try:
        reports = [analyze_rank(n) for n in args.ranks]
    except ValueError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    for report in reports:
        parameters = report["parameters"]
        residual = report["all_positive_residual"]
        status = "TRIVIAL" if not residual else "NON-TRIVIAL"
        print(
            f"n={report['n']}: all-positive profile {status}; "
            f"coboundary rank={report['coboundary_rank']}/"
            f"{report['coboundary_variables']}, "
            f"independent gb conditions={len(report['independent_conditions'])}"
        )
        for _, equation in report["independent_conditions"]:
            print(f"  condition: {_format_equation(equation, parameters)}")
        if residual:
            print("  all-positive residual witnesses:")
            for (x, y, z), coefficient in sorted(residual.items())[:12]:
                print(f"    ({x}, {y}) -> {z}: {coefficient}")
            if len(residual) > 12:
                print(f"    ... and {len(residual) - 12} additional residual entries")
        if report["trivial_profile"]:
            values = ", ".join(
                f"{name}={value}" for name, value in report["trivial_profile"].items()
            )
            print(f"  nonzero trivial gb profile: {values}")
        if len(parameters) <= 4:
            witness = report["scalar_witnesses"][0]
            print(
                "  scalar obstruction: "
                f"({witness['X']}, {witness['Y']}) -> K = "
                f"{witness['coeff']}*{witness['parameter']}*kappa"
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
