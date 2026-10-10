#!/usr/bin/env python3
"""Verify that the C(n+1) gb deformation tables are exact coboundaries."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import lsqr


ROOT = Path(__file__).resolve().parents[1]


def _load(path: Path) -> dict[str, object]:
    with path.open(encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return value


def _fraction(value: object) -> Fraction:
    if not isinstance(value, (str, int)):
        raise ValueError(f"Expected rational string or integer, got {value!r}")
    return Fraction(value)


def _add(target: dict[object, Fraction], key: object, value: Fraction) -> None:
    target[key] = target.get(key, Fraction()) + value
    if not target[key]:
        del target[key]


def _record_key(record: dict[str, object]) -> tuple[str, str, str]:
    try:
        left, right, output = record["X"], record["Y"], record["Z"]
    except KeyError as exc:
        raise ValueError(f"Missing bracket coordinate {exc.args[0]}") from exc
    if not all(isinstance(label, str) for label in (left, right, output)):
        raise ValueError(f"Invalid bracket coordinate: {record!r}")
    return left, right, output


def _exact_product(
    rows: list[dict[int, Fraction]], vector: dict[int, Fraction]
) -> dict[int, Fraction]:
    result: dict[int, Fraction] = {}
    for row_index, row in enumerate(rows):
        value = sum(
            (coefficient * vector.get(column, Fraction()) for column, coefficient in row.items()),
            Fraction(),
        )
        if value:
            result[row_index] = value
    return result


def _verify_rank(n: int) -> tuple[int, int]:
    gamma_data = _load(ROOT / f"data/C_{n}_gamma.json")
    evaluated_data = _load(ROOT / f"data/C_{n}_evaluated.json")
    coboundary_data = _load(ROOT / f"data/C_{n}_coboundary.json")

    if (
        gamma_data.get("schema_layer") != 2
        or evaluated_data.get("schema_layer") != 3
        or coboundary_data.get("schema_layer") != 4
    ):
        raise ValueError(f"n={n}: unexpected schema layers")

    basis_data = coboundary_data.get("basis")
    if not isinstance(basis_data, dict):
        raise ValueError(f"n={n}: invalid Layer 4 basis")
    basis = set(basis_data["even"]) | set(basis_data["odd"])

    assignment_data = evaluated_data.get("gb_assignment")
    if not isinstance(assignment_data, dict) or not isinstance(
        assignment_data.get("parameters"), dict
    ):
        raise ValueError(f"n={n}: invalid Layer 3 gb assignment")
    gb_parameters = list(assignment_data["parameters"])
    assigned_values = {
        parameter: _fraction(value)
        for parameter, value in assignment_data["parameters"].items()
    }

    gamma_records = gamma_data.get("gamma_constants")
    evaluated_records = evaluated_data.get("evaluated_constants")
    coboundary_records = coboundary_data.get("coboundary_constants")
    map_data = coboundary_data.get("odd_linear_map")
    if not all(
        isinstance(records, list)
        for records in (gamma_records, evaluated_records, coboundary_records)
    ) or not isinstance(map_data, dict) or not isinstance(
        map_data.get("coefficients"), list
    ):
        raise ValueError(f"n={n}: invalid coefficient tables")

    map_parameters = [
        entry["parameter"]
        for entry in map_data["coefficients"]
        if isinstance(entry, dict) and isinstance(entry.get("parameter"), str)
    ]
    if len(map_parameters) != len(map_data["coefficients"]):
        raise ValueError(f"n={n}: invalid odd-map parameter list")
    if len(set(map_parameters)) != len(map_parameters):
        raise ValueError(f"n={n}: duplicate odd-map parameter")

    row_keys: set[tuple[str, str, str]] = set()
    for record in coboundary_records:
        row_keys.add(_record_key(record))
    for record in gamma_records:
        key = _record_key(record)
        if key[2] in basis:
            row_keys.add(key)
    row_index = {key: index for index, key in enumerate(sorted(row_keys))}
    rows: list[dict[int, Fraction]] = [dict() for _ in row_index]
    parameter_index = {name: index for index, name in enumerate(map_parameters)}
    matrix_row_indices: list[int] = []
    matrix_column_indices: list[int] = []
    matrix_values: list[float] = []

    for record in coboundary_records:
        key = _record_key(record)
        terms = record.get("coeff")
        if not isinstance(terms, list):
            raise ValueError(f"n={n}: invalid Layer 4 terms at {key}")
        row = row_index[key]
        for term in terms:
            if not isinstance(term, dict) or term.get("parameter") not in parameter_index:
                raise ValueError(f"n={n}: invalid Layer 4 term at {key}: {term!r}")
            column = parameter_index[term["parameter"]]
            coefficient = _fraction(term.get("scalar"))
            _add(rows[row], column, coefficient)

    for row_number, row in enumerate(rows):
        for column, coefficient in row.items():
            matrix_row_indices.append(row_number)
            matrix_column_indices.append(column)
            matrix_values.append(float(coefficient))
    matrix = coo_matrix(
        (matrix_values, (matrix_row_indices, matrix_column_indices)),
        shape=(len(rows), len(map_parameters)),
        dtype=float,
    ).tocsr()

    gamma_vectors: dict[str, dict[int, Fraction]] = {
        parameter: {} for parameter in gb_parameters
    }
    for record in gamma_records:
        key = _record_key(record)
        if key[2] not in basis:
            continue
        terms = record.get("coeff")
        if not isinstance(terms, list):
            raise ValueError(f"n={n}: invalid Layer 2 terms at {key}")
        for term in terms:
            if (
                not isinstance(term, dict)
                or term.get("parameter") not in gamma_vectors
            ):
                raise ValueError(f"n={n}: invalid Layer 2 term at {key}: {term!r}")
            _add(
                gamma_vectors[term["parameter"]],
                row_index[key],
                _fraction(term.get("scalar")),
            )

    evaluated_vector: dict[int, Fraction] = {}
    scalar_count = 0
    for record in evaluated_records:
        key = _record_key(record)
        if key[2] not in basis:
            scalar_count += 1
            continue
        _add(evaluated_vector, row_index[key], _fraction(record.get("coeff")))

    reconstructed_evaluation: dict[int, Fraction] = {}
    for parameter, vector in gamma_vectors.items():
        value = assigned_values.get(parameter)
        if value is None:
            raise ValueError(f"n={n}: gb assignment is missing {parameter}")
        for row, coefficient in vector.items():
            _add(reconstructed_evaluation, row, value * coefficient)
    if reconstructed_evaluation != evaluated_vector:
        raise AssertionError(f"n={n}: Layer 2 does not reproduce Layer 3 exactly")

    witnesses: dict[str, dict[int, Fraction]] = {}
    for parameter in gb_parameters:
        target = gamma_vectors[parameter]
        numeric_target = np.zeros(len(rows), dtype=float)
        for row, coefficient in target.items():
            numeric_target[row] = float(coefficient)
        approximation = lsqr(
            matrix,
            numeric_target,
            atol=1e-14,
            btol=1e-14,
            iter_lim=20000,
        )[0]
        witness = {
            column: Fraction(float(value)).limit_denominator(100000)
            for column, value in enumerate(approximation)
        }
        witness = {
            column: value for column, value in witness.items() if value
        }
        if _exact_product(rows, witness) != target:
            raise AssertionError(
                f"n={n}: exact rational witness failed for {parameter}"
            )
        witnesses[parameter] = witness

    profile_witness: dict[int, Fraction] = {}
    for parameter, witness in witnesses.items():
        for column, value in witness.items():
            _add(
                profile_witness,
                column,
                assigned_values[parameter] * value,
            )
    if _exact_product(rows, profile_witness) != evaluated_vector:
        raise AssertionError(f"n={n}: profile witness failed exact substitution")

    lie_entry_count = len(evaluated_vector)
    print(
        f"n={n} C({n + 1}): rows={len(rows)}, map_parameters={len(map_parameters)}, "
        f"gb_parameters={len(gb_parameters)}, Layer3_Lie_rows={lie_entry_count}, "
        f"scalar_K_rows={scalar_count}"
    )
    for parameter, witness in witnesses.items():
        print(f"  exact: {parameter}; nonzero_f_coefficients={len(witness)}")
    print(
        f"  exact: Layer 3 profile={assignment_data.get('profile')}; "
        f"nonzero_f_coefficients={len(profile_witness)}"
    )
    return len(gb_parameters), len(witnesses)


def main() -> None:
    total_parameters = 0
    verified_parameters = 0
    for n in (1, 2, 3):
        total, verified = _verify_rank(n)
        total_parameters += total
        verified_parameters += verified
    if verified_parameters != total_parameters:
        raise AssertionError("Not all gb directions were verified")
    print(
        f"PASS: exact rational coboundary witnesses verified for "
        f"{verified_parameters}/{total_parameters} gb directions and "
        f"all three Layer 3 profiles."
    )


if __name__ == "__main__":
    main()
