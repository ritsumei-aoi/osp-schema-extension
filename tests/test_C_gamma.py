import json
from pathlib import Path

import pytest

from src.C_gamma import build_gamma_schema, output_path


@pytest.fixture(scope="module")
def gamma_schemas():
    return {
        n: build_gamma_schema(n, generation_date="2026-10-09")
        for n in (1, 2, 3)
    }


@pytest.mark.parametrize("n", (1, 2, 3))
def test_gb_matrix_and_corrected_parities(n, gamma_schemas):
    deformation = gamma_schemas[n]["inhomogeneous_deformation"]
    matrix = deformation["gb_matrix"]
    expected_columns = [
        label
        for index in range(1, n + 1)
        for label in (f"b_{index}_p", f"b_{index}_m")
    ]

    assert matrix["rows"] == ["a_1_p", "a_1_m"]
    assert matrix["columns"] == expected_columns
    assert len(matrix["entries"]) == 2
    assert all(len(row) == 2 * n for row in matrix["entries"])
    assert len({entry for row in matrix["entries"] for entry in row}) == 4 * n
    assert matrix["parity"] == 0
    relations = deformation["deformed_oscillator_relations"]
    assert relations["gb_parity"] == 0
    assert relations["kappa_parity"] == 1
    assert relations["relation"] == "[b_j^s, a_1^σ] = -gb_{σ,j,s} κ"


@pytest.mark.parametrize("n", (1, 2, 3))
def test_gamma_records_have_valid_labels_and_parity(n, gamma_schemas):
    gamma_schema = gamma_schemas[n]
    structure_path = Path("data") / f"C_{n}_structure.json"
    schema1 = json.loads(structure_path.read_text(encoding="utf-8"))
    basis_labels = set(schema1["basis"]["even"] + schema1["basis"]["odd"])
    output_labels = basis_labels | {"K"}
    parity = {**schema1["parity"], "K": 0}
    records = gamma_schema["inhomogeneous_deformation"]["gamma_coefficients"]
    parameters = {
        parameter
        for row in gamma_schema["inhomogeneous_deformation"]["gb_matrix"]["entries"]
        for parameter in row
    }

    assert records
    assert "K" not in basis_labels
    assert all(record["sign_rule"] == "graded" for record in records)
    for record in records:
        assert record["X"] in basis_labels
        assert record["Y"] in basis_labels
        assert record["Z"] in output_labels
        assert parity[record["Z"]] == (parity[record["X"]] ^ parity[record["Y"]] ^ 1)
        assert any(parameter in record["coeff"] for parameter in parameters)


def test_gamma_records_the_scalar_identity_contribution(gamma_schemas):
    records = gamma_schemas[1]["inhomogeneous_deformation"]["gamma_coefficients"]
    assert {
        (record["Z"], record["coeff"])
        for record in records
        if record["X"] == "E_eps1_del1_pp" and record["Y"] == "H_1"
    } >= {
        ("H_1", "gb_a1p_b1p"),
        ("K", "gb_a1p_b1p"),
    }


@pytest.mark.parametrize("n", (1, 2, 3))
def test_gamma_schema_serializes_and_uses_approved_filename(n, gamma_schemas):
    schema = gamma_schemas[n]
    assert schema["schema_version"] == "5.0"
    assert (
        schema["inhomogeneous_deformation"]["output_space"]
        == "Schema 1 basis plus central identity K."
    )
    assert set(schema) == {
        "schema_version",
        "algebra",
        "inhomogeneous_deformation",
        "metadata",
    }
    assert json.loads(json.dumps(schema, ensure_ascii=False)) == schema
    assert output_path(n, Path("data")).as_posix() == f"data/C_{n}_gamma.json"


@pytest.mark.parametrize("n", (1, 2, 3))
def test_generated_gamma_file_matches_computed_schema(n, gamma_schemas):
    path = Path("data") / f"C_{n}_gamma.json"
    generated = json.loads(path.read_text(encoding="utf-8"))
    assert generated == gamma_schemas[n]
