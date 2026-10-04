import json
from pathlib import Path

import pytest

from src.C_gamma import generate_gamma_schema


@pytest.mark.parametrize(("n", "expected_parameters"), [(1, 4), (2, 8), (3, 12)])
def test_gamma_schema_matches_rank_and_gb_matrix(n, expected_parameters):
    schema = generate_gamma_schema(n)
    deformation = schema["inhomogeneous_deformation"]
    matrix = schema["gb_matrix"]
    parameter_names = {
        parameter["name"] for parameter in matrix["parameters"]
    }

    assert matrix["shape"] == [2, 2 * n]
    assert len(matrix["parameters"]) == expected_parameters
    assert len(parameter_names) == expected_parameters
    assert all(parameter["parity"] == 0 for parameter in matrix["parameters"])
    assert all(
        item["gb_parameter"] in parameter_names
        and item["X"]
        and item["Y"]
        and item["Z"]
        and item["sign_rule"] == "graded"
        for item in deformation["gamma_coefficients"]
    )
    assert deformation["consistency"]["closure_with_central_identity_K"]
    assert deformation["consistency"]["all_outputs_in_schema_1_basis_or_K"]
    assert deformation["consistency"]["oscillator_relations_associative"]
    assert deformation["consistency"]["closure_failures"] == []
    assert deformation["consistency"]["central_identity_terms"] > 0
    assert not deformation["consistency"]["schema_1_basis_closed"]
    assert deformation["consistency"]["parameter_parity"] == 0
    assert "parity 0" in deformation["consistency"]["parameter_parity_decision"]
    from src.C_generators import _generator_data

    even, odd, _, _ = _generator_data(n)
    basis_parity = {label: 0 for label in even}
    basis_parity.update({label: 1 for label in odd})
    basis_parity["K"] = 0
    assert all(
        basis_parity[item["Z"]]
        == (basis_parity[item["X"]] + basis_parity[item["Y"]] + 1) % 2
        for item in deformation["gamma_coefficients"]
    )


@pytest.mark.parametrize("n", [1, 2, 3])
def test_generated_gamma_files_match_schema_contract(n):
    path = Path(__file__).parents[1] / "data" / f"C_{n}_gamma.json"
    schema = json.loads(path.read_text(encoding="utf-8"))
    assert schema["algebra"]["n"] == n
    assert schema["algebra"]["family"] == "C"
    assert schema["gb_matrix"]["shape"] == [2, 2 * n]
    assert schema["inhomogeneous_deformation"]["gamma_coefficients"]
    consistency = schema["inhomogeneous_deformation"]["consistency"]
    assert consistency["all_outputs_in_schema_1_basis_or_K"]
    assert consistency["oscillator_relations_associative"]


def test_gamma_generation_rejects_invalid_rank():
    with pytest.raises(ValueError, match="positive integer"):
        generate_gamma_schema(0)
