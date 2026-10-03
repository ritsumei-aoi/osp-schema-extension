from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.C_gamma import build_gamma_schema


EXPECTED_GAMMA_ROWS = {1: 112, 2: 652, 3: 1840}
EXPECTED_CENTRAL_ROWS = {1: 20, 2: 84, 3: 180}


@pytest.mark.parametrize("n", (1, 2, 3))
def test_gamma_schema_shape_and_coefficients(n: int) -> None:
    schema = build_gamma_schema(n)
    deformation = schema["inhomogeneous_deformation"]
    matrix = deformation["gb_matrix"]
    rows = deformation["gamma_coefficients"]
    structure = json.loads(
        (Path("data") / f"C_{n}_structure.json").read_text(encoding="utf-8")
    )
    generators = set(structure["basis"]["even"] + structure["basis"]["odd"])
    parameters = {
        parameter
        for row in matrix["entries"]
        for parameter in row
    }

    assert matrix["shape"] == [2, 2 * n]
    assert len(matrix["entries"]) == 2
    assert all(len(row) == 2 * n for row in matrix["entries"])
    assert len(parameters) == 4 * n
    assert deformation["parameter_parity"]["gb_scalar"] == 0
    assert deformation["parameter_parity"]["gb_times_kappa"] == 1
    assert len(rows) == EXPECTED_GAMMA_ROWS[n]
    assert sum(row["Z"] == "K" for row in rows) == EXPECTED_CENTRAL_ROWS[n]
    assert all(row["X"] in generators and row["Y"] in generators for row in rows)
    assert all(
        row["Z"] in generators | {"K"} and row["parameter"] in parameters
        for row in rows
    )
