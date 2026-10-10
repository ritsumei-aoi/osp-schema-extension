import json
from pathlib import Path

import pytest
import sympy as sp

from src.C_gamma_generator import build_gamma_schema


@pytest.mark.parametrize("n", [1, 2, 3])
def test_gamma_schema_matches_structure_basis_and_gb_dimensions(n):
    structure_path = Path("data") / f"C_{n}_structure.json"
    structure = json.loads(structure_path.read_text(encoding="utf-8"))
    schema = build_gamma_schema(n, structure, generation_date="2026-01-01")
    deformation = schema["inhomogeneous_deformation"]
    matrix = deformation["gb_matrix"]

    assert schema["source_structure_file"] == structure_path.name
    assert matrix["shape"] == [2, 2 * n]
    assert matrix["row_labels"] == ["a_1_p", "a_1_m"]
    assert len(matrix["column_labels"]) == 2 * n
    assert len(matrix["entries"]) == 2
    assert all(len(row) == 2 * n for row in matrix["entries"])
    assert matrix["parameter_parity"] == 0
    assert deformation["kappa"]["parity"] == 1
    assert deformation["gamma_coefficients"]


@pytest.mark.parametrize("n", [1, 2, 3])
def test_gamma_coefficients_have_correct_parity_and_skew_symmetry(n):
    structure = json.loads(
        (Path("data") / f"C_{n}_structure.json").read_text(encoding="utf-8")
    )
    schema = build_gamma_schema(n, structure)
    deformation = schema["inhomogeneous_deformation"]
    gamma = deformation["gamma_coefficients"]
    basis_parity = structure["parity"] | {"K": 0}
    coefficients = {
        (item["X"], item["Y"], item["Z"]): sp.sympify(item["coeff"])
        for item in gamma
    }
    allowed_parameters = {
        sp.Symbol(parameter)
        for row in deformation["gb_matrix"]["entries"]
        for parameter in row
    }

    for (left, right, result), coefficient in coefficients.items():
        assert basis_parity[result] == (
            structure["parity"][left] + structure["parity"][right] + 1
        ) % 2
        factor = 1 if structure["parity"][left] * structure["parity"][right] % 2 else -1
        assert coefficients[(right, left, result)] == factor * coefficient
        assert coefficient.free_symbols <= allowed_parameters


def test_gamma_includes_central_identity_component_when_present():
    structure = json.loads(
        Path("data/C_1_structure.json").read_text(encoding="utf-8")
    )
    gamma = build_gamma_schema(1, structure)["inhomogeneous_deformation"][
        "gamma_coefficients"
    ]

    assert any(entry["Z"] == "K" for entry in gamma)
